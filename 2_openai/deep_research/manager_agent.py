"""
Manager Agent - Orchestrates the deep research workflow using agents as tools
"""
from agents import Agent, Runner, function_tool, trace, gen_trace_id
from planner_agent import planner_agent, WebSearchPlan
from search_agent import search_agent
from writer_agent import writer_agent, ReportData
from email_agent import email_agent
from clarification_agent import clarification_agent, ClarificationQuestions
from typing import Dict
import asyncio


# Global storage for the report (so we can access it after the agent run)
_last_report = {"markdown_report": None}


# Tool wrappers for agents
@function_tool
async def generate_clarifying_questions(query: str) -> Dict:
    """
    Generate 3 clarifying questions to better understand the research needs.
    
    Args:
        query: The research query to generate questions for
        
    Returns:
        Dictionary with question1, question2, question3, and reasoning
    """
    print("🤔 Generating clarification questions...")
    result = await Runner.run(
        clarification_agent,
        f"Research query: {query}",
    )
    questions = result.final_output_as(ClarificationQuestions)
    print("✓ Questions generated")
    
    return {
        "question1": questions.question1,
        "question2": questions.question2,
        "question3": questions.question3,
        "reasoning": questions.reasoning
    }


@function_tool
async def plan_web_searches(query: str, clarifications: str = "") -> Dict:
    """
    Plan targeted web searches based on the query and clarifications.
    
    Args:
        query: The original research query
        clarifications: String containing Q&A pairs from clarification step (optional)
        
    Returns:
        Dictionary with list of searches (each has 'query' and 'reason')
    """
    print("📋 Planning web searches...")
    
    # Build input with explicit clarification structure
    input_text = f"Query: {query}"
    if clarifications:
        input_text += f"\n\n{clarifications}"
    
    result = await Runner.run(
        planner_agent,
        input_text,
    )
    plan = result.final_output_as(WebSearchPlan)
    print(f"✓ Planned {len(plan.searches)} searches")
    
    return {
        "searches": [
            {"query": item.query, "reason": item.reason}
            for item in plan.searches
        ]
    }


@function_tool
async def perform_web_search(search_query: str, reason: str) -> str:
    """
    Perform a single web search and return summarized results.
    
    Args:
        search_query: The search term to use
        reason: Why this search is important (for context)
        
    Returns:
        Summarized search results (2-3 paragraphs)
    """
    input_text = f"Search term: {search_query}\nReason for searching: {reason}"
    try:
        result = await Runner.run(
            search_agent,
            input_text,
        )
        return str(result.final_output)
    except Exception as e:
        return f"Search failed: {str(e)}"


@function_tool
async def write_research_report(query: str, search_results: str) -> Dict:
    """
    Write a comprehensive research report based on search results.
    
    Args:
        query: The original research query (with clarifications if any)
        search_results: Combined search results from all searches
        
    Returns:
        Dictionary with short_summary, markdown_report, and follow_up_questions
    """
    print("✍️ Writing comprehensive report...")
    
    input_text = f"Original query: {query}\nSummarized search results: {search_results}"
    result = await Runner.run(
        writer_agent,
        input_text,
    )
    
    report = result.final_output_as(ReportData)
    print("✓ Report completed")
    
    # Store the report globally so we can access it later
    _last_report["markdown_report"] = report.markdown_report
    _last_report["short_summary"] = report.short_summary
    _last_report["follow_up_questions"] = report.follow_up_questions
    
    # Debug: Confirm storage
    print(f"DEBUG: Stored report - markdown length: {len(report.markdown_report)}")
    print(f"DEBUG: Short summary: {report.short_summary[:100]}...")
    print(f"DEBUG: Follow-up questions: {len(report.follow_up_questions)}")
    
    return {
        "short_summary": report.short_summary,
        "markdown_report": report.markdown_report,
        "follow_up_questions": report.follow_up_questions
    }


@function_tool
async def send_research_email(markdown_report: str) -> Dict:
    """
    Send the research report via email.
    
    Args:
        markdown_report: The markdown-formatted report to send
        
    Returns:
        Dictionary with status
    """
    print("📧 Sending email...")
    
    result = await Runner.run(
        email_agent,
        markdown_report,
    )
    
    print("✓ Email sent")
    return {"status": "success"}


# Manager Agent Instructions
MANAGER_INSTRUCTIONS = """You are the Research Manager Agent. Your job is to orchestrate a comprehensive deep research process.

WORKFLOW:
1. **Clarification Phase** (OPTIONAL - only if user hasn't provided clarifications yet):
   - Use generate_clarifying_questions to create 3 questions
   - Return questions to user for answers
   - User will provide answers, then you continue

2. **Planning Phase**:
   - Use plan_web_searches with the query and clarifications (if any)
   - You'll receive a list of targeted searches to perform

3. **Search Phase**:
   - For EACH search in the plan, use perform_web_search
   - Call them in PARALLEL for efficiency (you can make multiple tool calls at once)
   - Collect all results

4. **Writing Phase**:
   - Use write_research_report with the query and ALL search results combined
   - You'll receive a comprehensive markdown report

5. **Email Phase**:
   - Use send_research_email to send the report
   - Confirm completion

6. **Final Output**:
   - After sending email, respond with a completion message that includes the report summary
   - Your final response should acknowledge the work is complete

IMPORTANT GUIDELINES:
- If clarifications are provided in the query, skip step 1 and go directly to planning
- When searching, you MUST call perform_web_search for EVERY search in the plan
- Combine all search results into a single string before writing the report
- Always complete all phases in order
- Provide brief status updates as you progress through each phase
- If any step fails, report the error clearly

CLARIFICATION FORMAT:
When clarifications are provided, they will look like:
"Clarifications (use these to create targeted searches):
Q: [question1]
A: [answer1]
Q: [question2]
A: [answer2]
Q: [question3]
A: [answer3]"

OUTPUT FORMAT:
Your responses should be informative and track progress. After completing all steps,
provide a brief completion message. The system will display the full report separately.
"""


def get_last_report() -> dict:
    """Retrieve the last generated report"""
    report_copy = _last_report.copy()
    print(f"DEBUG get_last_report: Returning report with {len(report_copy.get('markdown_report', '') or '')} chars")
    return report_copy


# Create the Manager Agent
manager_agent = Agent(
    name="ResearchManagerAgent",
    instructions=MANAGER_INSTRUCTIONS,
    model="gpt-4o",  # Use GPT-4o for better orchestration
    tools=[
        generate_clarifying_questions,
        plan_web_searches,
        perform_web_search,
        write_research_report,
        send_research_email,
    ],
)
