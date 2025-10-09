# Code Comparison: Before vs After Phase 3

## Architecture Evolution

### BEFORE: Python Class Orchestrator
```python
# research_manager.py (original)
class ResearchManager:
    
    async def run(self, query: str, clarifications: dict[str, str] | None = None):
        """Orchestrate research workflow manually"""
        
        # Manual orchestration - class methods
        search_plan = await self.plan_searches(query, clarifications)
        search_results = await self.perform_searches(search_plan)
        report = await self.write_report(enhanced_query, search_results)
        await self.send_email(report)
        
        return report.markdown_report
    
    async def plan_searches(self, query: str, clarifications: dict) -> WebSearchPlan:
        """Call planner agent directly"""
        result = await Runner.run(planner_agent, input_text)
        return result.final_output_as(WebSearchPlan)
    
    async def perform_searches(self, search_plan: WebSearchPlan) -> list[str]:
        """Manually orchestrate parallel searches"""
        tasks = [asyncio.create_task(self.search(item)) for item in search_plan.searches]
        results = []
        for task in asyncio.as_completed(tasks):
            result = await task
            results.append(result)
        return results
```

**Issues:**
- ❌ Manager is just a Python class, not an agent
- ❌ Hard-coded workflow logic
- ❌ No flexibility to adapt to different scenarios
- ❌ Manual error handling for each step
- ❌ Difficult to extend with new capabilities

---

### AFTER: Agent-Based with Tools
```python
# manager_agent.py (NEW!)
@function_tool
async def plan_web_searches(query: str, clarifications: str = "") -> Dict:
    """Plan targeted web searches based on the query and clarifications."""
    result = await Runner.run(planner_agent, input_text)
    plan = result.final_output_as(WebSearchPlan)
    return {
        "searches": [
            {"query": item.query, "reason": item.reason}
            for item in plan.searches
        ]
    }

@function_tool
async def perform_web_search(search_query: str, reason: str) -> str:
    """Perform a single web search and return summarized results."""
    result = await Runner.run(search_agent, input_text)
    return str(result.final_output)

@function_tool
async def write_research_report(query: str, search_results: str) -> Dict:
    """Write a comprehensive research report based on search results."""
    result = await Runner.run(writer_agent, input_text)
    report = result.final_output_as(ReportData)
    return {
        "short_summary": report.short_summary,
        "markdown_report": report.markdown_report,
        "follow_up_questions": report.follow_up_questions
    }

# Manager Agent with comprehensive instructions
MANAGER_INSTRUCTIONS = """You are the Research Manager Agent. 
Your job is to orchestrate a comprehensive deep research process.

WORKFLOW:
1. Planning Phase - Use plan_web_searches with query and clarifications
2. Search Phase - Call perform_web_search for EACH search (parallel is OK)
3. Writing Phase - Use write_research_report with all results
4. Email Phase - Use send_research_email to deliver report

IMPORTANT: You can make multiple tool calls in parallel for efficiency!
"""

manager_agent = Agent(
    name="ResearchManagerAgent",
    instructions=MANAGER_INSTRUCTIONS,
    model="gpt-4o",  # Intelligent orchestrator!
    tools=[
        generate_clarifying_questions,
        plan_web_searches,
        perform_web_search,
        write_research_report,
        send_research_email,
    ],
)
```

**Benefits:**
- ✅ Manager is now an intelligent Agent (GPT-4o)
- ✅ Sub-agents wrapped as tools
- ✅ Agent decides how to orchestrate workflow
- ✅ Flexible - can adapt to different scenarios
- ✅ Better error handling and recovery
- ✅ Easy to extend with new tools
- ✅ True agent handoffs

---

## Workflow Comparison

### BEFORE: Hard-coded Sequential Flow
```
User Query
    ↓
[ResearchManager.run()]
    ↓
plan_searches() → planner_agent
    ↓
perform_searches() → search_agent × N (parallel)
    ↓
write_report() → writer_agent
    ↓
send_email() → email_agent
    ↓
Done
```

### AFTER: Agent-Driven Adaptive Flow
```
User Query + Clarifications
    ↓
[manager_agent decides workflow]
    ↓
Calls plan_web_searches tool
    ↓ (tool wraps planner_agent)
Receives search plan
    ↓
[manager_agent intelligently orchestrates]
    ↓
Calls perform_web_search tool × N IN PARALLEL
    ↓ (each tool wraps search_agent)
Collects all results
    ↓
[manager_agent synthesizes]
    ↓
Calls write_research_report tool
    ↓ (tool wraps writer_agent)
Receives comprehensive report
    ↓
[manager_agent finalizes]
    ↓
Calls send_research_email tool
    ↓ (tool wraps email_agent)
Done ✅
```

**Key Difference:** Agent makes decisions at each step, not just following hard-coded logic!

---

## Example: How Agent Handles Errors

### BEFORE (Python Class):
```python
async def search(self, item: WebSearchItem) -> str | None:
    try:
        result = await Runner.run(search_agent, input)
        return str(result.final_output)
    except Exception:
        return None  # Silent failure
```

### AFTER (Agent with Tools):
```python
@function_tool
async def perform_web_search(search_query: str, reason: str) -> str:
    try:
        result = await Runner.run(search_agent, input_text)
        return str(result.final_output)
    except Exception as e:
        return f"Search failed: {str(e)}"
```

**Manager Agent can:**
- See the error message
- Decide to retry with different query
- Skip failed search and continue
- Adapt strategy based on partial results

---

## Example: Agent Intelligence in Action

### Scenario 1: User Already Provided Context
**Input:** "Research AI agent frameworks. I'm focused on production use, enterprise scale, and Python-based solutions."

**Before:** Would still generate clarification questions (wasted time)

**After:** Agent recognizes context is sufficient, skips clarification phase, goes straight to planning targeted searches!

### Scenario 2: Ambiguous Query
**Input:** "Tell me about agents"

**Before:** Would generate generic searches, waste API calls

**After:** Agent generates clarification questions first, then uses answers to create highly targeted searches

### Scenario 3: Search Failures
**Before:** Silent failures, missing data in final report

**After:** Agent sees which searches failed, can retry with modified queries, or note gaps in final report

---

## Streaming & Progress Comparison

### BEFORE: Manual Status Messages
```python
yield "Searches planned, starting to search..."
yield "Searches complete, writing report..."
yield "Report written, sending email..."
yield "Email sent, research complete"
```

### AFTER: Agent-Driven Status + Tool Tracking
```python
# ResearchManagerV2 tracks agent messages
for message in result.messages:
    if message.role == 'agent':
        yield f"{agent_thinking}\n\n"
    elif message.role == 'tool':
        if tool_name == 'plan_web_searches':
            yield "📋 Planning searches...\n"
        elif tool_name == 'perform_web_search':
            yield "🔍 Searching web...\n"
        # etc.
```

**Benefits:**
- See agent's reasoning
- Know which tools are executing
- Real-time progress updates
- Better user experience

---

## Extensibility Comparison

### Adding a New Capability

**BEFORE (Python Class):**
1. Add method to ResearchManager class
2. Update run() method to call new method
3. Handle errors manually
4. Update UI if needed
5. Test entire workflow

**AFTER (Agent Architecture):**
1. Create function_tool wrapper
2. Add tool to manager_agent.tools list
3. Update MANAGER_INSTRUCTIONS if needed
4. Agent automatically integrates new capability!

**Example - Adding Citation Extraction:**
```python
@function_tool
async def extract_citations(markdown_report: str) -> Dict:
    """Extract and format citations from report sources."""
    # ... implementation
    return {"citations": [...]}

# Add to tools list
manager_agent = Agent(
    name="ResearchManagerAgent",
    instructions=MANAGER_INSTRUCTIONS + "\nUse extract_citations before emailing.",
    tools=[
        ...,
        extract_citations,  # Just add it!
    ],
)
```

Done! Agent now knows when and how to use citations.

---

## Performance Comparison

### Parallel Search Execution

**BEFORE:**
```python
# Manual asyncio orchestration
tasks = [asyncio.create_task(self.search(item)) for item in searches]
results = []
for task in asyncio.as_completed(tasks):
    result = await task
    results.append(result)
```

**AFTER:**
```python
# Agent can call multiple tools in parallel!
# Just documented in instructions:
"""
IMPORTANT: For efficiency, you can call perform_web_search 
multiple times in parallel (multiple tool calls at once).
"""
```

Agent automatically handles parallelization based on context!

---

## Summary

| Aspect | Before (Class) | After (Agent) |
|--------|---------------|---------------|
| **Orchestration** | Manual, hard-coded | Intelligent, adaptive |
| **Flexibility** | Fixed workflow | Dynamic decisions |
| **Error Handling** | Manual try/catch | Agent-driven recovery |
| **Extensibility** | Requires code changes | Add tools + instructions |
| **Observability** | Manual logging | Full trace integration |
| **Parallelization** | Manual asyncio | Agent-driven optimization |
| **Intelligence** | None (just function calls) | GPT-4o reasoning |
| **Handoffs** | Direct function calls | True agent handoffs |

---

## The Power of Agents-as-Tools Pattern

**Key Insight:** By converting sub-agents into tools, we give the manager agent the **ability to reason about when and how to use specialized capabilities**, rather than blindly following a hard-coded script.

This is the future of agentic systems! 🚀
