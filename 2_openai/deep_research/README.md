# Deep Research - AI-Powered Research Assistant

A sophisticated research application that uses OpenAI's Agents SDK to conduct comprehensive web research with intelligent clarification, targeted search planning, and detailed report generation.

## 🌟 Features

### Three-Phase Enhancement System

#### **Phase 1: Clarification System** ⭐
- Generates 3 intelligent clarifying questions before research begins
- Understands user intent and refines research focus
- Creates targeted searches based on clarifications
- Two-step UI workflow: Questions → Research

#### **Phase 2: Enhanced Planner** 🎯
- Context-aware search planning
- Uses clarifications to create highly specific search queries
- Tailors searches to user's intended use case and audience
- Optimizes for relevance over generic coverage

#### **Phase 3: Agent Architecture** 🏗️
- Fully agent-based system using agents-as-tools pattern
- Manager agent orchestrates 5 specialized sub-agents
- Each agent wrapped as a `@function_tool` for composability
- GPT-4o orchestration with GPT-4o-mini specialized agents

### Core Capabilities

- **Intelligent Clarification**: Asks targeted questions to understand research needs
- **Web Search**: Parallel web searches using OpenAI's WebSearchTool
- **Comprehensive Reports**: 5-10 page markdown reports (1000+ words)
- **Email Delivery**: Automatic email with formatted HTML report
- **Streaming UI**: Real-time progress updates in Gradio interface
- **Trace Logging**: OpenAI platform trace links for debugging

## 🏛️ Architecture

### Agent-Based System (Phase 3)

```
┌─────────────────────────────────────────────────────────────┐
│                     Manager Agent (GPT-4o)                  │
│  Orchestrates workflow, calls tools, manages state          │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ calls tools
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                      Function Tools                          │
│  Each wraps a specialized agent as a function                │
├──────────────────────────────────────────────────────────────┤
│  1. generate_clarifying_questions → clarification_agent      │
│  2. plan_web_searches            → planner_agent            │
│  3. perform_web_search           → search_agent             │
│  4. write_research_report        → writer_agent             │
│  5. send_research_email          → email_agent              │
└──────────────────────────────────────────────────────────────┘
```

### File Structure

```
deep_research/
├── deep_research.py           # Gradio UI (two-step workflow)
├── research_manager_v2.py     # Agent-based manager wrapper
├── manager_agent.py           # Core orchestrator with 5 function_tools
├── clarification_agent.py     # Generates 3 clarifying questions
├── planner_agent.py           # Plans targeted web searches
├── search_agent.py            # Performs web searches
├── writer_agent.py            # Writes comprehensive reports
├── email_agent.py             # Sends HTML emails via SendGrid
├── research_manager.py        # [Legacy] Class-based orchestrator
├── PHASE3_COMPLETE.md         # Phase 3 documentation
├── BEFORE_AFTER_COMPARISON.md # Architecture comparison
└── README.md                  # This file
```

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- OpenAI API key
- SendGrid API key (for email delivery)
- `uv` package manager

### Installation

1. **Clone the repository**
```bash
cd 2_openai/deep_research
```

2. **Set up environment variables**

Create a `.env` file in the `2_openai/deep_research` directory:

```env
OPENAI_API_KEY=your_openai_api_key_here
SENDGRID_API_KEY=your_sendgrid_api_key_here
```

3. **Configure email addresses**

Edit `email_agent.py` to set your sender and recipient:

```python
from_email = Email("your_verified_sender@gmail.com")
to_email = To("recipient@example.com")
```

> **Note**: SendGrid requires sender email verification. See [SendGrid Sender Verification](https://docs.sendgrid.com/ui/sending-email/sender-verification).

### Running the Application

```bash
uv run deep_research.py
```

The application will launch in your default browser at `http://127.0.0.1:7860`.

## 📖 Usage

### Two-Step Workflow

#### Step 1: Enter Query & Answer Questions
1. Enter your research query (e.g., "AI applications in material engineering")
2. Click **"Generate Clarification Questions"**
3. Answer the 3 clarifying questions to refine focus

#### Step 2: Run Research
1. Click **"Start Research"**
2. Watch real-time progress updates
3. View comprehensive report in UI
4. Receive formatted report via email

### Example Research Flow

**Query**: "What are the research frontiers of agent AI applications to material engineering?"

**Clarification Questions**:
1. What specific areas within material engineering interest you? (design, testing, manufacturing)
2. Are you looking for recent advancements, ongoing projects, or theoretical frameworks?
3. Who is your target audience? (researchers, professionals, policymakers)

**Answers**:
1. Material design
2. Recent advancements
3. Academic researchers

**Result**: 5 targeted web searches → Comprehensive 6000+ character report → Email delivery

## 🛠️ Technical Details

### Agent Configuration

| Agent | Model | Role | Output Type |
|-------|-------|------|-------------|
| Manager | GPT-4o | Orchestrator | Tool calls |
| Clarification | GPT-4o-mini | Question generator | `ClarificationQuestions` |
| Planner | GPT-4o-mini | Search planner | `WebSearchPlan` |
| Search | GPT-4o-mini | Web searcher | Text summary |
| Writer | GPT-4o-mini | Report writer | `ReportData` |
| Email | GPT-4o-mini | Email sender | Success status |

### Structured Outputs

```python
class ClarificationQuestions(BaseModel):
    reasoning: str
    question1: str
    question2: str
    question3: str

class WebSearchPlan(BaseModel):
    searches: list[WebSearchItem]  # 5 searches

class ReportData(BaseModel):
    short_summary: str              # 2-3 sentences
    markdown_report: str            # 1000+ words
    follow_up_questions: list[str]  # 3 questions
```

### Global Storage Pattern

To retrieve reports after agent execution:

```python
# In manager_agent.py
_last_report = {"markdown_report": None}

@function_tool
async def write_research_report(...) -> Dict:
    # ... generate report ...
    _last_report["markdown_report"] = report.markdown_report
    return {...}

def get_last_report() -> dict:
    return _last_report.copy()
```

### Streaming Output Pattern

To display progressive content in Gradio:

```python
# Accumulate output for Gradio (each yield replaces content)
accumulated_output = ""
accumulated_output += "Starting...\n"
yield accumulated_output

accumulated_output += "Complete!\n"
yield accumulated_output
```

## 🔍 Debugging & Monitoring

### OpenAI Traces

Every research run generates a trace link:
```
View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}
```

Visit this link to see:
- Agent reasoning steps
- Tool calls and responses
- Token usage
- Latency metrics

### Debug Logging

The application includes extensive debug logging:
```python
DEBUG: Stored report - markdown length: 6385
DEBUG: Short summary: Recent advancements...
DEBUG: Follow-up questions: 3
DEBUG get_last_report: Returning report with 6385 chars
DEBUG: Retrieved report_data keys: dict_keys([...])
DEBUG: markdown_report length: 6385
```

### Common Issues

**Issue**: "Report not displaying in UI"
- **Cause**: Gradio yields replacing instead of accumulating
- **Solution**: Use accumulated output pattern (see code)

**Issue**: "AttributeError: 'RunResult' has no attribute 'messages'"
- **Cause**: Trying to access non-existent result attributes
- **Solution**: Use global storage pattern for cross-function data

**Issue**: "SendGrid 403 Forbidden"
- **Cause**: Sender email not verified in SendGrid
- **Solution**: Verify sender in SendGrid dashboard

## 📊 Performance

- **Average Research Time**: 30-60 seconds
- **Searches**: 5 parallel web searches
- **Report Length**: 5-10 pages (1000-2000 words)
- **Token Usage**: ~15,000-30,000 tokens per research
- **Cost**: ~$0.15-0.30 per research (GPT-4o + GPT-4o-mini)

## 🔄 Development Evolution

### Phase 1: Basic Research
- Single-step process
- Generic web searches
- Class-based orchestration

### Phase 2: Clarification System
- Two-step workflow
- User-guided research focus
- Clarification-aware planning

### Phase 3: Agent Architecture
- Agents-as-tools pattern
- Manager orchestration
- Full composability
- Production-ready architecture

## 📝 API Keys & Configuration

### Required Environment Variables

```bash
# OpenAI API Key (required)
OPENAI_API_KEY=sk-proj-...

# SendGrid API Key (required for email)
SENDGRID_API_KEY=SG....
```

### Optional Configuration

Edit constants in respective files:
- `planner_agent.py`: `HOW_MANY_SEARCHES` (default: 5)
- `search_agent.py`: `search_context_size` (default: "low")
- `writer_agent.py`: Report length guidelines (default: 5-10 pages)

## 🤝 Contributing

This is part of an AI agents learning repository. Feel free to:
- Experiment with different agent configurations
- Add new specialized agents
- Modify search strategies
- Enhance report formatting

## 📄 License

See the repository root for license information.

## 🙏 Acknowledgments

- Built with [OpenAI Agents SDK](https://platform.openai.com/docs/agents)
- UI powered by [Gradio](https://gradio.app/)
- Email delivery via [SendGrid](https://sendgrid.com/)

## 📚 Further Reading

- `PHASE3_COMPLETE.md` - Detailed Phase 3 implementation guide
- `BEFORE_AFTER_COMPARISON.md` - Architecture evolution comparison
- [OpenAI Agents Documentation](https://platform.openai.com/docs/agents)
- [Agents-as-Tools Pattern](https://platform.openai.com/docs/agents/tools)

---

**Built with ❤️ using OpenAI Agents SDK**
