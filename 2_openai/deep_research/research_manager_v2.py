"""
Research Manager V2 - Agent-based architecture with streaming
"""
from agents import Runner, trace, gen_trace_id
from manager_agent import manager_agent
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
            yield "🚀 Starting research workflow...\n\n"
            yield "📋 Manager agent is orchestrating the research process...\n"
            yield "⏳ This may take a few minutes as we plan, search, and write the report...\n\n"
            
            try:
                result = await Runner.run(
                    manager_agent,
                    input_text,
                )
                
                # Extract the final output from the agent
                final_output = result.final_output
                
                yield "✅ Research complete!\n\n"
                
                if final_output:
                    # Check if the output contains useful information
                    if isinstance(final_output, str):
                        # If it's a string response, show it
                        yield "---\n\n"
                        yield f"{final_output}\n\n"
                        yield "---\n\n"
                    
                yield "📧 The comprehensive research report has been sent to your email.\n"
                yield "🔍 View the full trace at the link above to see all agent actions.\n"
                    
            except Exception as e:
                yield f"\n\n❌ Error during research: {str(e)}\n"
                print(f"Error: {e}")
                import traceback
                traceback.print_exc()
