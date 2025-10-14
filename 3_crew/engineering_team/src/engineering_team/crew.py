from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from typing import Tuple, Any
import ast
from engineering_team.specs import SystemPlan


# ============================================================================
# Guardrail Functions (Challenge D)
# ============================================================================

def guard_raw_python(result) -> Tuple[bool, Any]:
    """
    Guardrail to ensure output is raw Python code without markdown fences.
    Returns (is_valid, processed_output)
    """
    out = result.raw if hasattr(result, 'raw') else str(result)

    if "```" in out:
        return (False, "Remove markdown fences; output must be raw Python code")

    return (True, out)


def guard_valid_syntax(result) -> Tuple[bool, Any]:
    """
    Guardrail to validate Python syntax.
    Returns (is_valid, processed_output)
    """
    out = result.raw if hasattr(result, 'raw') else str(result)

    try:
        ast.parse(out)
        return (True, out)
    except SyntaxError as e:
        return (False, f"Invalid Python syntax: {str(e)}")


# ============================================================================
# Callback Functions (Challenge E)
# ============================================================================

def on_task_complete(output):
    """
    Callback fired after task completion for observability.
    Logs completion metrics and artifact paths.
    """
    agent_name = output.agent if hasattr(output, 'agent') else "Unknown"
    desc = output.description if hasattr(output, 'description') else "N/A"
    raw_preview = (output.raw[:200] + "...") if hasattr(output, 'raw') and output.raw else "No output"

    print(f"\n{'='*60}")
    print(f"[TASK COMPLETE] Agent: {agent_name}")
    print(f"Description: {desc}")
    print(f"Output Preview: {raw_preview}")
    print(f"{'='*60}\n")



@CrewBase
class EngineeringTeam():
    """EngineeringTeam crew"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def engineering_lead(self) -> Agent:
        return Agent(
            config=self.agents_config['engineering_lead'],
            verbose=True,
        )

    @agent
    def backend_engineer(self) -> Agent:
        return Agent(
            config=self.agents_config['backend_engineer'],
            verbose=True,
            allow_code_execution=True,
            code_execution_mode="safe",  # Uses Docker for safety
            max_execution_time=500, 
            max_retry_limit=3 
        )
    
    @agent
    def frontend_engineer(self) -> Agent:
        return Agent(
            config=self.agents_config['frontend_engineer'],
            verbose=True,
        )
    
    @agent
    def test_engineer(self) -> Agent:
        return Agent(
            config=self.agents_config['test_engineer'],
            verbose=True,
            allow_code_execution=True,
            code_execution_mode="safe",  # Uses Docker for safety
            max_execution_time=500,
            max_retry_limit=3
        )

    @agent
    def business_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['business_analyst'],
            verbose=True,
        )

    @agent
    def qa_planner(self) -> Agent:
        return Agent(
            config=self.agents_config['qa_planner'],
            verbose=True,
        )

    @agent
    def devops_engineer(self) -> Agent:
        return Agent(
            config=self.agents_config['devops_engineer'],
            verbose=True,
        )

    @agent
    def security_reviewer(self) -> Agent:
        return Agent(
            config=self.agents_config['security_reviewer'],
            verbose=True,
        )

    @task
    def design_task(self) -> Task:
        return Task(
            config=self.tasks_config['design_task'],
            output_pydantic=SystemPlan,
            callback=on_task_complete
        )

    @task
    def code_task(self) -> Task:
        return Task(
            config=self.tasks_config['code_task'],
            guardrail=guard_raw_python,
            callback=on_task_complete
        )

    @task
    def frontend_task(self) -> Task:
        return Task(
            config=self.tasks_config['frontend_task'],
            guardrail=guard_raw_python,
            callback=on_task_complete
        )

    @task
    def test_task(self) -> Task:
        return Task(
            config=self.tasks_config['test_task'],
            guardrail=guard_raw_python,
            callback=on_task_complete
        )

    @task
    def ba_task(self) -> Task:
        return Task(
            config=self.tasks_config['ba_task'],
            callback=on_task_complete
        )

    @task
    def qa_plan_task(self) -> Task:
        return Task(
            config=self.tasks_config['qa_plan_task'],
            callback=on_task_complete
        )

    @task
    def devops_task(self) -> Task:
        return Task(
            config=self.tasks_config['devops_task'],
            callback=on_task_complete
        )

    @task
    def security_review_task(self) -> Task:
        return Task(
            config=self.tasks_config['security_review_task'],
            callback=on_task_complete
        )

    @crew
    def crew(self) -> Crew:
        """Creates the research crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            max_rpm=30,  # Limit to 30 requests per minute
            # memory=False,  # Disable memory to reduce token usage
        )