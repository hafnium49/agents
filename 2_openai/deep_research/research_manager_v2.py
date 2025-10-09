"""
Research Manager V2 - Agent-based architecture with streaming
"""
from agents import Runner, trace, gen_trace_id
from manager_agent import manager_agent, get_last_report
from clarification_agent import clarification_agent, ClarificationQuestions
import asyncio


class ResearchManagerV2:
    """
    Agent-based research manager that orchestrates the research workflow
    using the manager_agent with agents-as-tools
    """
    
    async def generate_clarification_questions(self, query: str) -> ClarificationQuestions:
        """Generate 3 clarifying questions based on the research query"""
        print("Generating clarification questions...")
        result = await Runner.run(
            clarification_agent,
            f"Research query: {query}",
        )
        print("Questions generated")
        return result.final_output_as(ClarificationQuestions)
    
    async def run(self, query: str, clarifications: dict[str, str] | None = None):
        """
        Run the deep research process using the manager agent.
        Yields status updates and the final report.
        """
        trace_id = gen_trace_id()
        with trace("Research trace", trace_id=trace_id):
            print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}")
            yield f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}\n\n"
            
            # Build input for manager agent
            input_text = f"Research query: {query}"
            
            if clarifications:
                clarification_context = "\n\nClarifications (use these to create targeted searches):\n"
                for q, a in clarifications.items():
                    clarification_context += f"Q: {q}\nA: {a}\n"
                input_text += clarification_context
                yield "✓ Using clarifications to refine research...\n\n"
            
            # Run the manager agent
            # Accumulate all output so each yield replaces with growing content
            accumulated_output = ""
            
            accumulated_output += "🚀 Starting research workflow...\n\n"
            yield accumulated_output
            
            try:
                result = await Runner.run(
                    manager_agent,
                    input_text,
                )
                
                # Check if agent has a final message
                if hasattr(result, 'final_output') and result.final_output:
                    agent_message = str(result.final_output)
                    if agent_message and len(agent_message) < 500:  # Only show if it's a short message
                        accumulated_output += f"\n🤖 Agent: {agent_message}\n\n"
                        yield accumulated_output
                
                accumulated_output += "✅ Research complete!\n\n"
                yield accumulated_output
                
                # Get the report from the global storage
                report_data = get_last_report()
                
                # Debug: Print what we got
                print(f"DEBUG: Retrieved report_data keys: {report_data.keys()}")
                print(f"DEBUG: markdown_report length: {len(report_data.get('markdown_report', '')) if report_data.get('markdown_report') else 0}")
                
                markdown_report = report_data.get('markdown_report')
                short_summary = report_data.get('short_summary')
                follow_up = report_data.get('follow_up_questions', [])
                
                # Display the report
                if markdown_report and len(markdown_report) > 100:  # Make sure it's substantial
                    accumulated_output += "\n---\n\n"
                    
                    # Show short summary first if available
                    if short_summary:
                        accumulated_output += f"**Summary:** {short_summary}\n\n"
                        accumulated_output += "\n"
                    
                    accumulated_output += "# Research Report\n\n"
                    accumulated_output += markdown_report
                    accumulated_output += "\n\n---\n\n"
                    
                    # Show follow-up questions if available
                    if follow_up and len(follow_up) > 0:
                        accumulated_output += "\n## 📌 Suggested Follow-up Topics:\n\n"
                        for i, question in enumerate(follow_up, 1):
                            accumulated_output += f"{i}. {question}\n"
                        accumulated_output += "\n"
                    
                    yield accumulated_output
                else:
                    accumulated_output += "⚠️ Report generation completed but content not found or too short. Check your email for the full report.\n"
                    yield accumulated_output
                    print(f"WARNING: markdown_report is None, empty, or too short! Length: {len(markdown_report) if markdown_report else 0}")
                    print(f"DEBUG: Full report_data: {report_data}")
                    
            except Exception as e:
                accumulated_output += f"\n\n❌ Error during research: {str(e)}\n"
                yield accumulated_output
                print(f"Error: {e}")
                import traceback
                traceback.print_exc()
