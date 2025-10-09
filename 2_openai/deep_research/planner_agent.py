from pydantic import BaseModel, Field
from agents import Agent

HOW_MANY_SEARCHES = 5

INSTRUCTIONS = f"""You are a helpful research assistant. Given a query, come up with a set of web searches \
to perform to best answer the query. Output {HOW_MANY_SEARCHES} terms to query for.

IMPORTANT: If clarification questions and answers are provided, use them to create MORE TARGETED and SPECIFIC searches.
The clarifications reveal the user's true intent, specific focus areas, and intended use case.

For example:
- If clarifications indicate focus on "technical implementation", prioritize searches about code, architecture, best practices
- If clarifications indicate focus on "business impact", prioritize searches about ROI, case studies, market trends  
- If clarifications mention specific use cases, tailor searches to those scenarios
- If clarifications reveal constraints (budget, timeline, scale), factor those into search planning

Your goal is to generate searches that directly address the clarified needs, not generic searches."""


class WebSearchItem(BaseModel):
    reason: str = Field(description="Your reasoning for why this search is important to the query.")
    query: str = Field(description="The search term to use for the web search.")


class WebSearchPlan(BaseModel):
    searches: list[WebSearchItem] = Field(description="A list of web searches to perform to best answer the query.")
    
planner_agent = Agent(
    name="PlannerAgent",
    instructions=INSTRUCTIONS,
    model="gpt-4o-mini",
    output_type=WebSearchPlan,
)