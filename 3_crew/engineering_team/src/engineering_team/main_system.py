#!/usr/bin/env python
"""
Dynamic multi-module system builder (Challenge C)

This demonstrates how to:
1. Get a typed SystemPlan from the design task
2. Dynamically generate tasks per ModuleSpec
3. Use async_execution for parallel builds
4. Add final aggregator task for determinism
"""

import sys
import warnings
import os
from datetime import datetime

from crewai import Task, Crew, Process
from engineering_team.crew import EngineeringTeam, on_task_complete, guard_raw_python
from engineering_team.specs import SystemPlan

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


def build_system(requirements: str, module_name: str = "system.py", class_name: str = "System"):
    """
    Build a complete system with dynamic task generation based on SystemPlan.

    Args:
        requirements: High-level system requirements
        module_name: Default module name (can be overridden by SystemPlan)
        class_name: Default class name
    """
    # Create output directory
    os.makedirs('output', exist_ok=True)

    # Initialize the team
    team = EngineeringTeam()

    # Step 1: Get the typed plan from design task
    print("\n" + "="*80)
    print("PHASE 1: Getting SystemPlan from design task...")
    print("="*80 + "\n")

    design_task_instance = team.design_task()

    # Create a minimal crew to execute just the design task
    design_crew = Crew(
        agents=[team.engineering_lead()],
        tasks=[design_task_instance],
        process=Process.sequential,
        verbose=True,
    )

    inputs = {
        'requirements': requirements,
        'module_name': module_name,
        'class_name': class_name
    }

    design_result = design_crew.kickoff(inputs=inputs)

    # Extract the SystemPlan (structured output)
    try:
        plan: SystemPlan = design_result.pydantic
        print(f"\n✓ SystemPlan received: {len(plan.modules)} module(s)")
        for mod in plan.modules:
            print(f"  - {mod.name}: {len(mod.classes)} class(es), UI={mod.needs_ui_demo}, Tests={mod.needs_tests}")
    except Exception as e:
        print(f"\n✗ Failed to parse SystemPlan: {e}")
        print("Falling back to original module_name...")
        # Fallback: treat as single module
        plan = None

    if not plan or not plan.modules:
        print("\n⚠ No modules in plan, using default single-module build")
        return run_single_module_build(team, requirements, module_name, class_name)

    # Step 2: Dynamic task generation per module
    print("\n" + "="*80)
    print("PHASE 2: Generating tasks dynamically per module...")
    print("="*80 + "\n")

    generated_tasks = []
    be = team.backend_engineer()
    fe = team.frontend_engineer()
    tester = team.test_engineer()
    ba = team.business_analyst()
    qa = team.qa_planner()
    devops = team.devops_engineer()
    sec = team.security_reviewer()

    # Business Analyst task (runs early)
    ba_task_instance = team.ba_task()
    generated_tasks.append(ba_task_instance)

    # For each module in the plan, create code/test/UI tasks
    for module_spec in plan.modules:
        module_file = module_spec.name

        # Code task for this module
        code_task = Task(
            description=f"Implement module {module_file} per SystemPlan. Classes: {', '.join([c.name for c in module_spec.classes])}",
            expected_output=f"{module_file} - raw Python code (no markdown fences).",
            agent=be,
            async_execution=True,  # Parallel build
            context=[design_task_instance],  # Depends on design
            guardrail=guard_raw_python,
            callback=on_task_complete,
            output_file=f"output/{module_file}"
        )
        generated_tasks.append(code_task)

        # Test task (if needed)
        if module_spec.needs_tests:
            test_task = Task(
                description=f"Write comprehensive unit tests for {module_file}.",
                expected_output=f"test_{module_file} - raw Python code with pytest tests.",
                agent=tester,
                async_execution=True,
                context=[code_task],  # Depends on code
                guardrail=guard_raw_python,
                callback=on_task_complete,
                output_file=f"output/test_{module_file}"
            )
            generated_tasks.append(test_task)

        # UI demo task (if needed)
        if module_spec.needs_ui_demo:
            ui_task = Task(
                description=f"Create a minimal Gradio demo for {module_file}.",
                expected_output=f"app_{module_file.replace('.py', '')}.py - Gradio UI code.",
                agent=fe,
                async_execution=True,
                context=[code_task],  # Depends on code
                guardrail=guard_raw_python,
                callback=on_task_complete,
                output_file=f"output/app_{module_file.replace('.py', '')}.py"
            )
            generated_tasks.append(ui_task)

    # QA Plan task (depends on design)
    qa_task_instance = team.qa_plan_task()
    generated_tasks.append(qa_task_instance)

    # Security Review task (depends on all code tasks)
    sec_task_instance = team.security_review_task()
    generated_tasks.append(sec_task_instance)

    # DevOps task (depends on all code/test/UI tasks)
    devops_task_instance = team.devops_task()
    generated_tasks.append(devops_task_instance)

    # Step 3: Final aggregator task (for determinism)
    print(f"\n✓ Generated {len(generated_tasks)} tasks")

    summary_task = Task(
        description="Summarize all modules, link artifacts, and provide run instructions in a comprehensive README.",
        expected_output="README.md with setup, usage, testing, and deployment instructions.",
        agent=team.engineering_lead(),
        context=generated_tasks,  # Wait for all async tasks
        callback=on_task_complete,
        output_file="output/README.md"
    )

    # Step 4: Create and run the full crew
    print("\n" + "="*80)
    print("PHASE 3: Running full crew with all tasks...")
    print("="*80 + "\n")

    full_crew = Crew(
        agents=[team.engineering_lead(), be, fe, tester, ba, qa, devops, sec],
        tasks=[design_task_instance, *generated_tasks, summary_task],
        process=Process.sequential,
        verbose=True,
        max_rpm=30,
    )

    result = full_crew.kickoff(inputs=inputs)

    print("\n" + "="*80)
    print("✓ System build complete!")
    print("="*80 + "\n")

    return result


def run_single_module_build(team, requirements, module_name, class_name):
    """
    Fallback: Run the original single-module sequential build.
    """
    print("\nRunning single-module build (original workflow)...")

    inputs = {
        'requirements': requirements,
        'module_name': module_name,
        'class_name': class_name
    }

    # Use the standard crew
    result = team.crew().kickoff(inputs=inputs)

    return result


def run():
    """
    Main entry point for the dynamic system builder.
    """
    requirements = """
A simple account management system for a trading simulation platform.
The system should allow users to create an account, deposit funds, and withdraw funds.
The system should allow users to record that they have bought or sold shares, providing a quantity.
The system should calculate the total value of the user's portfolio, and the profit or loss from the initial deposit.
The system should be able to report the holdings of the user at any point in time.
The system should be able to report the profit or loss of the user at any point in time.
The system should be able to list the transactions that the user has made over time.
The system should prevent the user from withdrawing funds that would leave them with a negative balance, or
 from buying more shares than they can afford, or selling shares that they don't have.
The system has access to a function get_share_price(symbol) which returns the current price of a share,
and includes a test implementation that returns fixed prices for AAPL, TSLA, GOOGL.
"""

    module_name = "accounts.py"
    class_name = "Account"

    result = build_system(requirements, module_name, class_name)

    print(f"\n{'='*80}")
    print("Final Result:")
    print(f"{'='*80}")
    print(result)


if __name__ == "__main__":
    run()
