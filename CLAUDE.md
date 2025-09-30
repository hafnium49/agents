# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an educational repository for the "Agentic AI Engineering" course - a 6-week program teaching AI agent development using multiple frameworks. The codebase uses Python 3.12 and the `uv` package manager.

## Repository Structure

The repository is organized by weekly modules, each covering a different AI agent framework:
- `1_foundations/` - Basic LLM API calls and patterns
- `2_openai/` - OpenAI Agents SDK
- `3_crew/` - CrewAI multi-agent framework
- `4_langgraph/` - LangGraph state machines
- `5_autogen/` - Microsoft AutoGen framework
- `6_mcp/` - Model Context Protocol

Each week contains 4 lab notebooks (`1_lab1.ipynb` through `4_lab4.ipynb`) and example applications.

## Essential Commands

### Environment Setup
```bash
uv sync                    # Install/update all dependencies
uv python install 3.12     # Install Python 3.12 if needed
```

### Running Code
```bash
uv run <script.py>         # Run any Python script
uv run jupyter notebook    # Launch Jupyter notebooks
```

### CrewAI Projects (Week 3)
```bash
cd 3_crew/<project_name>
crewai install            # Install crew-specific dependencies
crewai run                # Run the crew
```

### Running Interactive Apps
Most weeks have Gradio-based demo apps:
```bash
uv run app.py             # Launch interactive UI (usually on port 7860)
```

## Architecture Patterns

### Multi-Agent Systems
The course progressively builds complexity:
1. **Simple API Calls** (Week 1): Direct OpenAI/Anthropic API usage
2. **Single Agents** (Week 2): Tool-calling agents with tracing
3. **Agent Teams** (Week 3-4): Multi-agent collaboration with CrewAI/LangGraph
4. **Conversational Agents** (Week 5): AutoGen's group chat pattern
5. **Protocol-Based** (Week 6): MCP server-client architecture

### Common Implementation Patterns

**Environment Configuration**: All projects use `.env` files for API keys:
```
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...
GOOGLE_API_KEY=...
```

**CrewAI Projects Structure**:
```
3_crew/<project>/
├── agents.yaml       # Agent role definitions
├── tasks.yaml        # Task specifications
├── crew.py          # Main crew orchestration
└── tools/           # Custom tool implementations
```

**LangGraph State Machines**:
- Use `StateGraph` for workflow definition
- SQLite checkpointing for state persistence
- Async operations for concurrent tasks

**MCP Servers** (Week 6):
- Server implementations in `server.py`
- Client connections via stdio protocol
- Tool registration and remote execution

### Key Dependencies

The project uses `uv` package manager with dependencies defined in `pyproject.toml`:
- **LLM SDKs**: openai, anthropic, openai-agents
- **Frameworks**: autogen-agentchat, langchain, langgraph, mcp
- **UI**: gradio for interactive demos
- **Web**: playwright, bs4 for web scraping
- **Data**: pypdf for document processing

### Development Tips

1. **Jupyter Notebooks**: Primary interface for labs - run cells sequentially
2. **API Keys**: Always check `.env` configuration before running code
3. **Framework Updates**: Use `uv sync` to ensure dependencies are current
4. **CrewAI CLI**: Available via `uv tool install crewai` for crew management
5. **Memory/State**: LangGraph uses SQLite, CrewAI has built-in memory options
6. **Community Examples**: Check `community_contributions/` in each week for alternative implementations

### Common Troubleshooting

- **Import Errors**: Run `uv sync` to ensure all dependencies installed
- **API Errors**: Verify API keys in `.env` file
- **CrewAI Issues**: Use `crewai install` inside crew project directories
- **Port Conflicts**: Gradio apps default to port 7860; kill existing processes if needed
- **Memory Issues**: Clear SQLite databases in `memory/` folder if corrupted