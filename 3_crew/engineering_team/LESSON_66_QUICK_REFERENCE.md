# Lesson 66 Quick Reference Card

## Challenge Checklist

### ✅ Challenge A: Grow the Team (YAML-first)
**Requirement:** Add 4 new agent roles with YAML configuration

**Implementation:**
- [agents.yaml](src/engineering_team/config/agents.yaml#L49-L96):
  - `business_analyst` → Requirements clarification
  - `qa_planner` → Risk-based test planning
  - `devops_engineer` → CI/CD automation
  - `security_reviewer` → Vulnerability scanning

- [tasks.yaml](src/engineering_team/config/tasks.yaml#L54-L126):
  - `ba_task` → `output/requirements.md`
  - `qa_plan_task` → `output/test_plan.md`
  - `devops_task` → `output/devops.md`
  - `security_review_task` → `output/security_review.md`

**Where to verify:**
```bash
cat src/engineering_team/config/agents.yaml | grep -A 10 "business_analyst:"
cat src/engineering_team/config/tasks.yaml | grep -A 8 "ba_task:"
```

---

### ✅ Challenge B: Structured Outputs (output_pydantic)
**Requirement:** Design task returns typed SystemPlan

**Implementation:**
- [specs.py](src/engineering_team/specs.py) - Pydantic models:
  ```python
  class SystemPlan(BaseModel):
      modules: List[ModuleSpec]
      notes: str
  ```

- [crew.py](src/engineering_team/crew.py#L104-L109) - Task config:
  ```python
  @task
  def design_task(self) -> Task:
      return Task(
          config=self.tasks_config['design_task'],
          output_pydantic=SystemPlan,  # ← Structured output
      )
  ```

**Where to verify:**
```bash
uv run python -c "from engineering_team.specs import SystemPlan; print(SystemPlan.model_json_schema())"
```

---

### ✅ Challenge C: Dynamic Multi-Module Build
**Requirement:** Fan out tasks based on SystemPlan, use async execution

**Implementation:**
- [main_system.py](src/engineering_team/main_system.py#L85-L140) - Dynamic task generation:
  ```python
  for module_spec in plan.modules:
      code_task = Task(
          description=f"Implement {module_spec.name}",
          async_execution=True,  # ← Parallel build
          context=[design_task],
      )
  ```

- Final aggregator task waits for all async tasks:
  ```python
  summary_task = Task(
      context=generated_tasks,  # ← Wait for all
      output_file="output/README.md"
  )
  ```

**Where to verify:**
```bash
uv run python -m engineering_team.main_system  # Run full dynamic build
```

---

### ✅ Challenge D: Guardrails
**Requirement:** Function-based validators with auto-retry

**Implementation:**
- [crew.py](src/engineering_team/crew.py#L12-L36) - Guardrail functions:
  ```python
  def guard_raw_python(result) -> Tuple[bool, Any]:
      if "```" in out:
          return (False, "Remove markdown fences")
      return (True, out)
  ```

- Applied to tasks:
  ```python
  Task(
      guardrail=guard_raw_python,  # ← Validator
      # Auto-retries up to 3 times (default)
  )
  ```

**Where to verify:**
```bash
grep -n "guardrail=" src/engineering_team/crew.py
```

---

### ✅ Challenge E: Callbacks
**Requirement:** Task-level callbacks for observability

**Implementation:**
- [crew.py](src/engineering_team/crew.py#L43-L56) - Callback function:
  ```python
  def on_task_complete(output):
      print(f"[TASK COMPLETE] {output.agent}")
  ```

- Attached to all tasks:
  ```python
  Task(
      callback=on_task_complete,  # ← Fires after completion
  )
  ```

**Where to verify:**
```bash
grep -n "callback=" src/engineering_team/crew.py
```

---

### ✅ Challenge F: Markdown Formatting
**Requirement:** Use `markdown: true` for narrative outputs

**Implementation:**
- [tasks.yaml](src/engineering_team/config/tasks.yaml):
  ```yaml
  ba_task:
    markdown: true  # ← Auto-formatting
    output_file: output/requirements.md

  qa_plan_task:
    markdown: true
    output_file: output/test_plan.md
  ```

**Where to verify:**
```bash
grep -B 2 "markdown: true" src/engineering_team/config/tasks.yaml
```

---

## Key Files Map

| File | Purpose | Lesson 66 Features |
|------|---------|-------------------|
| [specs.py](src/engineering_team/specs.py) | Pydantic models | Challenge B (structured outputs) |
| [agents.yaml](src/engineering_team/config/agents.yaml) | Agent definitions | Challenge A (4 new agents) |
| [tasks.yaml](src/engineering_team/config/tasks.yaml) | Task definitions | Challenge A (4 new tasks), F (markdown) |
| [crew.py](src/engineering_team/crew.py) | Crew logic | Challenges D (guardrails), E (callbacks) |
| [main_system.py](src/engineering_team/main_system.py) | Dynamic builder | Challenge C (async, fan-out) |

---

## Testing the Implementation

### 1. Verify Imports
```bash
uv run python -c "
from engineering_team.crew import EngineeringTeam, guard_raw_python, on_task_complete
from engineering_team.specs import SystemPlan
print('✓ All imports successful')
"
```

### 2. Run Single-Module Build
```bash
uv run python -m engineering_team.main
# Check output/accounts.py, output/app.py, etc.
```

### 3. Run Dynamic Multi-Module Build
```bash
uv run python -m engineering_team.main_system
# Check output/requirements.md, test_plan.md, devops.md, security_review.md
```

### 4. Verify Guardrails
```bash
# Guardrails auto-retry if code has markdown fences
# Check crew.py lines 115, 123, 131 for guardrail assignments
```

### 5. Check Callbacks
```bash
# Run any build and look for "[TASK COMPLETE]" logs
uv run python -m engineering_team.main 2>&1 | grep "TASK COMPLETE"
```

---

## CrewAI Spec Compliance

| CrewAI Feature | Used? | Location |
|----------------|-------|----------|
| `output_pydantic` | ✅ | crew.py:107 |
| `output_json` | ❌ | (using pydantic instead) |
| `output_file` | ✅ | All tasks in tasks.yaml |
| `markdown: true` | ✅ | tasks.yaml (ba, qa, devops, security) |
| `async_execution` | ✅ | main_system.py:105 |
| `context: [...]` | ✅ | tasks.yaml + main_system.py |
| `guardrail` | ✅ | crew.py:115,123,131 |
| `callback` | ✅ | All tasks in crew.py |
| `create_directory` | ✅ | Default (auto-creates output/) |

---

## Performance Notes

- **Sequential mode** (main.py): ~5-10 min for 4 tasks
- **Dynamic mode** (main_system.py): ~8-15 min for 8+ tasks (parallel builds)
- **Rate limits**: Set to 30 RPM (crew.py:198)
- **LLM usage**:
  - Design/BA/QA: GPT-4o (better reasoning)
  - Code/Tests: Claude Sonnet (better code generation)
  - DevOps/Security: GPT-4o-mini (cost-effective)

---

## Next Steps

1. **Run the examples** to see all features in action
2. **Customize requirements** in main.py or main_system.py
3. **Add custom tools** to agents for your domain (database, APIs, etc.)
4. **Switch to hierarchical mode** for dynamic agent assignment
5. **Integrate with Week 6** - Use as code-gen service in larger pipelines

---

## Troubleshooting

**Q: Guardrail keeps failing**
A: Check LLM outputs in verbose logs. Some LLMs ignore "no markdown fences" instructions. Increase retries or switch LLM.

**Q: SystemPlan not parsing**
A: Verify design task LLM returns valid JSON. main_system.py has fallback to single-module build.

**Q: Async tasks hanging**
A: Ensure final task has all async tasks in `context=[...]`. Check for circular dependencies.

**Q: Missing dependencies in generated code**
A: Review `output/devops.md` for install commands. Add to pyproject.toml if persistent.

---

**Full Documentation:** [IMPLEMENTATION.md](IMPLEMENTATION.md)
**CrewAI Tasks Docs:** https://docs.crewai.com/en/concepts/tasks
