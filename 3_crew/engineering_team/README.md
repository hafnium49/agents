# EngineeringTeam Crew

Welcome to the **EngineeringTeam Crew** - a production-grade multi-agent system implementing **Lesson 66 Challenge Pack** features with CrewAI.

This crew builds complete software systems with:
- **8 specialized agents** (Engineering Lead, Backend/Frontend/Test Engineers, Business Analyst, QA Planner, DevOps, Security Reviewer)
- **Structured outputs** via Pydantic models for type-safe system plans
- **Guardrails** to enforce code quality contracts
- **Callbacks** for observability and progress tracking
- **Dynamic task generation** for multi-module projects
- **Async execution** for parallel builds

See [IMPLEMENTATION.md](IMPLEMENTATION.md) for complete details on Lesson 66 challenge implementations.

## Installation

Ensure you have Python >=3.10 <3.13 installed on your system. This project uses [UV](https://docs.astral.sh/uv/) for dependency management and package handling, offering a seamless setup and execution experience.

First, if you haven't already, install uv:

```bash
pip install uv
```

Next, navigate to your project directory and install the dependencies:

(Optional) Lock the dependencies and install them by using the CLI command:
```bash
crewai install
```
### Customizing

**Add your `OPENAI_API_KEY` into the `.env` file**

- Modify `src/engineering_team/config/agents.yaml` to define your agents
- Modify `src/engineering_team/config/tasks.yaml` to define your tasks
- Modify `src/engineering_team/crew.py` to add your own logic, tools and specific args
- Modify `src/engineering_team/main.py` to add custom inputs for your agents and tasks

## Running the Project

### Mode 1: Single-Module Build (Original)

Build a single Python module with code, tests, and UI:

```bash
cd 3_crew/engineering_team
crewai run
# OR
uv run python -m engineering_team.main
```

**Outputs:** `output/{module_name}`, `output/app.py`, `output/test_{module_name}`, `output/{module_name}_design.md`

### Mode 2: Dynamic Multi-Module System (NEW - Lesson 66)

Build complete systems with dynamic task generation based on SystemPlan:

```bash
uv run python -m engineering_team.main_system
# OR
uv run run_system
```

**Additional Outputs:**
- `output/requirements.md` - Business requirements analysis
- `output/test_plan.md` - QA test strategy
- `output/devops.md` - Deployment runbook with `uv` commands
- `output/security_review.md` - Security vulnerability report
- `output/README.md` - Comprehensive system documentation

### Testing Generated Code

```bash
# Run unit tests
uv run pytest output/test_*.py

# Run Gradio UI
uv run python output/app.py
```

## Understanding Your Crew

The engineering_team Crew features **8 specialized agents**:

| Agent | Role | Output |
|-------|------|--------|
| **Engineering Lead** | System design & architecture | SystemPlan (typed JSON) + design.md |
| **Backend Engineer** | Python implementation | Module code with guardrails |
| **Frontend Engineer** | Gradio UI demos | Interactive web apps |
| **Test Engineer** | Unit testing | Pytest test suites |
| **Business Analyst** | Requirements analysis | requirements.md |
| **QA Planner** | Test strategy | test_plan.md |
| **DevOps Engineer** | CI/CD automation | devops.md with uv commands |
| **Security Reviewer** | Vulnerability scanning | security_review.md |

### Key Features (Lesson 66)

✅ **Structured Outputs** - Design task returns typed `SystemPlan` via Pydantic
✅ **Guardrails** - Code tasks enforce "no markdown fences" with auto-retry
✅ **Callbacks** - All tasks log completion metrics for observability
✅ **Async Tasks** - Parallel code/test/UI generation in dynamic mode
✅ **Markdown Outputs** - Narrative docs auto-formatted (requirements, QA, security, DevOps)

See [IMPLEMENTATION.md](IMPLEMENTATION.md) for technical details.

## Support

For support, questions, or feedback regarding the EngineeringTeam Crew or crewAI.
- Visit our [documentation](https://docs.crewai.com)
- Reach out to us through our [GitHub repository](https://github.com/joaomdmoura/crewai)
- [Join our Discord](https://discord.com/invite/X4JWnZnxPb)
- [Chat with our docs](https://chatg.pt/DWjSBZn)

Let's create wonders together with the power and simplicity of crewAI.
