# Engineering Team - Lesson 66 Implementation Guide

## Overview

This implementation extends the basic engineering crew with production-grade features based on **Lesson 66 Challenge Pack** and **CrewAI Tasks specification**.

## What's New (Challenges Completed)

### ✅ Challenge A: Expanded Team
Added 4 new specialized roles:
- **Business Analyst** - Requirements clarification and acceptance criteria
- **QA Planner** - Risk-based test strategy and planning
- **DevOps Engineer** - CI/CD automation and runbooks
- **Security Reviewer** - Vulnerability scanning and secure coding

### ✅ Challenge B: Structured Outputs
- Created Pydantic models (`specs.py`): `SystemPlan`, `ModuleSpec`, `ClassSpec`
- Design task now emits **typed, validated JSON** via `output_pydantic`
- Enables machine-readable plans for dynamic task generation

### ✅ Challenge C: Dynamic Multi-Module System Builder
- New `main_system.py` orchestrator
- Parses `SystemPlan` and dynamically creates tasks per module
- **Sequential execution** with proper task dependencies (Note: CrewAI doesn't allow async tasks to depend on other async tasks)
- Final aggregator task ensures deterministic completion

### ✅ Challenge D: Guardrails
- `guard_raw_python()` - Enforces no markdown fences in code outputs
- `guard_valid_syntax()` - Validates Python syntax (available but not enforced)
- Applied to `code_task`, `frontend_task`, `test_task`
- Auto-retry up to 3 times on guardrail failure

### ✅ Challenge E: Callbacks
- `on_task_complete()` - Logs completion metrics for observability
- Attached to all tasks for progress tracking
- Shows agent name, description, and output preview

### ✅ Challenge F: Markdown Formatting
- Enabled `markdown: true` for narrative outputs:
  - Design documents
  - Requirements docs
  - QA plans
  - Security reviews
  - DevOps runbooks

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Engineering Team Crew                     │
├─────────────────────────────────────────────────────────────┤
│ Agents (8):                                                  │
│  • Engineering Lead    • Backend Engineer                    │
│  • Frontend Engineer   • Test Engineer                       │
│  • Business Analyst    • QA Planner                          │
│  • DevOps Engineer     • Security Reviewer                   │
├─────────────────────────────────────────────────────────────┤
│ Tasks (Sequential Mode):                                     │
│  1. BA Task         → requirements.md                        │
│  2. Design Task     → SystemPlan (JSON) + design.md          │
│  3. Code Task       → module.py (+ guardrail)                │
│  4. Frontend Task   → app.py (+ guardrail)                   │
│  5. Test Task       → test_module.py (+ guardrail)           │
│  6. QA Plan Task    → test_plan.md                           │
│  7. DevOps Task     → devops.md                              │
│  8. Security Task   → security_review.md                     │
├─────────────────────────────────────────────────────────────┤
│ Dynamic Mode (main_system.py):                               │
│  1. Design → SystemPlan                                      │
│  2. For each ModuleSpec:                                     │
│     - Code task (sequential, depends on design)              │
│     - Test task (sequential, depends on code)                │
│     - UI task (sequential, depends on code)                  │
│  3. BA, QA, Security, DevOps tasks                           │
│  4. Final aggregator → README.md                             │
└─────────────────────────────────────────────────────────────┘
```

## File Structure

```
engineering_team/
├── src/engineering_team/
│   ├── config/
│   │   ├── agents.yaml          # 8 agent definitions (4 new)
│   │   └── tasks.yaml           # 8 task definitions (4 new)
│   ├── crew.py                  # Main crew + guardrails + callbacks
│   ├── specs.py                 # Pydantic models (NEW)
│   ├── main.py                  # Original single-module runner
│   └── main_system.py           # Dynamic multi-module builder (NEW)
├── output/                      # Generated artifacts
│   ├── requirements.md
│   ├── {module_name}_design.md
│   ├── {module_name}
│   ├── app.py
│   ├── test_{module_name}
│   ├── test_plan.md
│   ├── devops.md
│   ├── security_review.md
│   └── README.md (if using main_system.py)
├── pyproject.toml               # Added pydantic dependency
└── IMPLEMENTATION.md            # This file
```

## Usage

### 1. Install Dependencies

```bash
cd 3_crew/engineering_team
uv sync
```

### 2. Run Original Single-Module Build

```bash
uv run python -m engineering_team.main
# OR
crewai run
```

**Output:**
- `output/{module_name}_design.md` - Design document (markdown + SystemPlan JSON)
- `output/{module_name}` - Python module
- `output/app.py` - Gradio UI
- `output/test_{module_name}` - Unit tests

### 3. Run Dynamic Multi-Module Build (NEW)

```bash
uv run python -m engineering_team.main_system
# OR
uv run run_system
```

**Output (extended):**
- All outputs from single-module build, PLUS:
- `output/requirements.md` - BA requirements analysis
- `output/test_plan.md` - QA test strategy
- `output/devops.md` - Deployment runbook
- `output/security_review.md` - Security findings
- `output/README.md` - Comprehensive system summary

### 4. Customize Requirements

Edit the `requirements` string in [main.py](src/engineering_team/main.py#L14) or [main_system.py](src/engineering_team/main_system.py#L167).

## Key Implementation Details

### Pydantic Models (specs.py)

```python
class ClassSpec(BaseModel):
    name: str
    public_methods: List[str]
    description: str

class ModuleSpec(BaseModel):
    name: str
    classes: List[ClassSpec]
    functions: List[str]
    needs_ui_demo: bool = False
    needs_tests: bool = True
    dependencies: List[str]

class SystemPlan(BaseModel):
    modules: List[ModuleSpec]
    notes: str
    system_name: str
    requirements_summary: str
```

### Guardrails (crew.py)

```python
def guard_raw_python(result) -> Tuple[bool, Any]:
    """Ensures no markdown fences in code outputs"""
    out = result.raw if hasattr(result, 'raw') else str(result)
    if "```" in out:
        return (False, "Remove markdown fences; output must be raw Python code")
    return (True, out)
```

Applied via:
```python
Task(
    config=self.tasks_config['code_task'],
    guardrail=guard_raw_python,  # Auto-retry up to 3x
    callback=on_task_complete
)
```

### Callbacks (crew.py)

```python
def on_task_complete(output):
    """Logs task completion for observability"""
    print(f"[TASK COMPLETE] Agent: {output.agent}")
    print(f"Output Preview: {output.raw[:200]}...")
```

### Task Dependencies (main_system.py)

```python
code_task = Task(
    description=f"Implement module {module_file}",
    agent=backend_engineer,
    async_execution=False,  # Sequential to allow dependent tasks
    context=[design_task],  # Wait for design
    guardrail=guard_raw_python,
    output_file=f"output/{module_file}"
)
```

**Important:** CrewAI validation prevents async tasks from depending on other async tasks. Use sequential execution with `context=[...]` for proper dependency management.

## Acceptance Criteria (DoD)

| Challenge | Criteria | Status |
|-----------|----------|--------|
| A | 4 new agents (BA, QA, DevOps, Security) added | ✅ |
| B | Design emits `SystemPlan` via `output_pydantic` | ✅ |
| C | Dynamic fan-out per `ModuleSpec` | ✅ |
| C | Sequential execution with task dependencies | ✅ |
| D | Guardrails enforce contracts (raw Python) | ✅ |
| E | Callbacks for observability | ✅ |
| F | `markdown: true` for narrative outputs | ✅ |
| - | Artifacts land in `output/` predictably | ✅ |
| - | Final crew output = summary task output | ✅ |

## Next Steps

1. **Test the system:**
   ```bash
   uv run python -m engineering_team.main_system
   ```

2. **Review generated artifacts** in `output/`:
   - Check `security_review.md` for vulnerabilities
   - Follow `devops.md` instructions to run the app
   - Execute tests: `uv run pytest output/test_*.py`

3. **Extend for your use case:**
   - Modify `requirements` for your domain (materials science, lab automation, etc.)
   - Add custom tools to agents (web scraping, database access, etc.)
   - Switch to `Process.hierarchical` for unknown module counts

4. **Integrate with Week 6 patterns:**
   - Use this crew as a code-generation microservice
   - Feed outputs to LangGraph state machines
   - Expose via MCP server for Claude Code integration

## Troubleshooting

**Issue:** Guardrail failures on code tasks
**Solution:** Check LLM is not wrapping code in markdown fences. The guardrail will auto-retry 3x.

**Issue:** SystemPlan not parsing
**Solution:** Verify design task LLM outputs valid JSON. Falls back to single-module build.

**Issue:** Missing dependencies in generated code
**Solution:** Review `devops.md` for `uv` install commands. Add to `pyproject.toml` if needed.

**Issue:** "Async task cannot depend on async task" validation error
**Solution:** CrewAI doesn't allow async tasks in the context of other async tasks. Use `async_execution=False` for tasks with dependencies.

## References

- [CrewAI Tasks Documentation](https://docs.crewai.com/en/concepts/tasks)
- [Lesson 66 Challenge Pack](./LESSON_66.md) (if saved)
- [Original Engineering Team](./src/engineering_team/main.py)
- [Week 3 Course Materials](../../README.md)
