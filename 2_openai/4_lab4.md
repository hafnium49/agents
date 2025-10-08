## Deep Research

One of the classic cross-business Agentic use cases! This is huge.

<table style="margin: 0; text-align: left; width:100%">
    <tr>
        <td style="width: 150px; height: 150px; vertical-align: middle;">
            <img src="../assets/business.png" width="150" height="150" style="display: block;" />
        </td>
        <td>
            <h2 style="color:#00bfff;">Commercial implications</h2>
            <span style="color:#00bfff;">A Deep Research agent is broadly applicable to any business area, and to your own day-to-day activities. You can make use of this yourself!
            </span>
        </td>
    </tr>
</table>


```python
from agents import Agent, WebSearchTool, trace, Runner, gen_trace_id, function_tool
from agents.model_settings import ModelSettings
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import asyncio
import sendgrid
import os
from sendgrid.helpers.mail import Mail, Email, To, Content
from typing import Dict
from IPython.display import display, Markdown
```


```python
load_dotenv(override=True)
```




    True



## OpenAI Hosted Tools

OpenAI Agents SDK includes the following hosted tools:

The `WebSearchTool` lets an agent search the web.  
The `FileSearchTool` allows retrieving information from your OpenAI Vector Stores.  
The `ComputerTool` allows automating computer use tasks like taking screenshots and clicking.

### Important note - API charge of WebSearchTool

This is costing me 2.5 cents per call for OpenAI WebSearchTool. That can add up to $2-$3 for the next 2 labs. We'll use free and low cost Search tools with other platforms, so feel free to skip running this if the cost is a concern. Also student Christian W. pointed out that OpenAI can sometimes charge for multiple searches for a single call, so it could sometimes cost more than 2.5 cents per call.

Costs are here: https://platform.openai.com/docs/pricing#web-search


```python
INSTRUCTIONS = "You are a research assistant. Given a search term, you search the web for that term and \
produce a concise summary of the results. The summary must 2-3 paragraphs and less than 300 \
words. Capture the main points. Write succintly, no need to have complete sentences or good \
grammar. This will be consumed by someone synthesizing a report, so it's vital you capture the \
essence and ignore any fluff. Do not include any additional commentary other than the summary itself."

search_agent = Agent(
    name="Search agent",
    instructions=INSTRUCTIONS,
    tools=[WebSearchTool(search_context_size="low")],
    model="gpt-4o-mini",
    model_settings=ModelSettings(tool_choice="required"),
)
```


```python
message = "Latest AI Agent frameworks in 2025"

with trace("Search"):
    result = await Runner.run(search_agent, message)

display(Markdown(result.final_output))
```


In 2025, several AI agent frameworks have emerged, each offering unique features to enhance the development and deployment of intelligent agents.

**Agent Lightning** introduces a flexible framework for training AI agents using Reinforcement Learning (RL). It decouples agent execution from training, allowing seamless integration with existing agents and supporting complex interactions like multi-agent scenarios. ([arxiv.org](https://arxiv.org/abs/2508.03680?utm_source=openai))

**Polymorphic Combinatorial Framework (PCF)** focuses on designing adaptive AI agents grounded in mathematical principles. By leveraging combinatorial logic and fuzzy set theory, PCF enables real-time reconfiguration of agent behaviors, facilitating scalability and adaptability in dynamic environments. ([arxiv.org](https://arxiv.org/abs/2508.01581?utm_source=openai))

**Cognitive Kernel-Pro** is an open-source, multi-module agent framework aimed at democratizing advanced AI agent development. It emphasizes the curation of high-quality training data and introduces novel strategies for agent test-time reflection, achieving state-of-the-art results among open-source agents. ([arxiv.org](https://arxiv.org/abs/2508.00414?utm_source=openai))

**AutoAgent** offers a fully automated, zero-code framework for Large Language Model (LLM) agents. Designed to be accessible to users without technical backgrounds, AutoAgent enables the creation and deployment of LLM agents through natural language interfaces, supporting dynamic creation and modification of tools and workflows. ([arxiv.org](https://arxiv.org/abs/2502.05957?utm_source=openai))

**OpenAI Agents SDK** is a lightweight Python framework released in March 2025, focusing on creating multi-agent workflows with comprehensive tracing and guardrails. It is provider-agnostic, compatible with over 100 different LLMs, and offers detailed monitoring and debugging capabilities. ([jlcnews.com](https://www.jlcnews.com/post/the-best-ai-agents-in-2025-tools-frameworks-and-platforms-compared?utm_source=openai))

**Google Agent Development Kit (ADK)** is a modular framework announced in April 2025, integrating with the Google ecosystem, including Gemini and Vertex AI. It supports hierarchical agent compositions and requires minimal code for efficient development. ([jlcnews.com](https://www.jlcnews.com/post/the-best-ai-agents-in-2025-tools-frameworks-and-platforms-compared?utm_source=openai))

**Amazon Bedrock AgentCore** is a platform unveiled by AWS in August 2025, designed to simplify the development and deployment of advanced AI agents. It includes modular services supporting the full production lifecycle, emphasizing flexibility and scalability. ([techradar.com](https://www.techradar.com/pro/aws-looks-to-super-charge-ai-agents-with-amazon-bedrock-agentcore?utm_source=openai))

**Microsoft Semantic Kernel** is an open-source framework that bridges traditional development with AI capabilities, emphasizing seamless integration into enterprise applications. It supports multiple programming languages and offers orchestrators for managing multi-step AI workflows. ([signitysolutions.com](https://www.signitysolutions.com/blog/top-ai-agent-frameworks?utm_source=openai))

**Microsoft AutoGen** is an open-source framework for building sophisticated multi-agent systems, simplifying the development of conversational AI and task automation agents. ([signitysolutions.com](https://www.signitysolutions.com/blog/top-ai-agent-frameworks?utm_source=openai))

**Kruti** is a multilingual AI agent and chatbot developed by the Indian company Ola Krutrim, designed to perform real-world tasks by integrating directly with various online services. It supports text and voice in 13 Indian languages and is optimized for smartphone usage, addressing the Indian market's specific needs. ([en.wikipedia.org](https://en.wikipedia.org/wiki/Kruti?utm_source=openai))

**Manus** is China's first fully autonomous AI agent, capable of operating independently based on large language models. It can autonomously handle complex tasks, including writing and deploying code, marking a significant advancement in AI agent capabilities. ([en.wikipedia.org](https://en.wikipedia.org/wiki/Manus_%28AI_agent%29?utm_source=openai))

These frameworks reflect the rapid evolution in AI agent development, offering diverse tools and capabilities to meet various application needs. 


### As always, take a look at the trace

https://platform.openai.com/traces

### We will now use Structured Outputs, and include a description of the fields


```python
# See note above about cost of WebSearchTool

HOW_MANY_SEARCHES = 3

INSTRUCTIONS = f"You are a helpful research assistant. Given a query, come up with a set of web searches \
to perform to best answer the query. Output {HOW_MANY_SEARCHES} terms to query for."

# Use Pydantic to define the Schema of our response - this is known as "Structured Outputs"
# With massive thanks to student Wes C. for discovering and fixing a nasty bug with this!

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
```


```python

message = "Latest AI Agent frameworks in 2025"

with trace("Search"):
    result = await Runner.run(planner_agent, message)
    print(result.final_output)
```

    searches=[WebSearchItem(reason='To find updated information on the most popular AI agent frameworks in 2025.', query='latest AI agent frameworks 2025'), WebSearchItem(reason='To see a comparison of features, advantages, and use cases of different AI frameworks released or updated in 2025.', query='top AI frameworks comparison 2025'), WebSearchItem(reason='To gather insights from industry experts and publications on the trends in AI agent development as of 2025.', query='AI agent development trends 2025')]



```python
@function_tool
def send_email(subject: str, html_body: str) -> Dict[str, str]:
    """ Send out an email with the given subject and HTML body """
    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email("hafnium49@gmail.com")  # Email("ed@edwarddonner.com")  # Change to your verified sender
    to_email = To("chemistry49@hotmail.co.jp")  # To("ed.donner@gmail.com")  # Change to your recipient
    content = Content("text/html", html_body)
    mail = Mail(from_email, to_email, subject, content).get()
    response = sg.client.mail.send.post(request_body=mail)
    return {"status": "success"}
```


```python
send_email
```




    FunctionTool(name='send_email', description='Send out an email with the given subject and HTML body', params_json_schema={'properties': {'subject': {'title': 'Subject', 'type': 'string'}, 'html_body': {'title': 'Html Body', 'type': 'string'}}, 'required': ['subject', 'html_body'], 'title': 'send_email_args', 'type': 'object', 'additionalProperties': False}, on_invoke_tool=<function function_tool.<locals>._create_function_tool.<locals>._on_invoke_tool at 0x7f0470339c60>, strict_json_schema=True, is_enabled=True)




```python
INSTRUCTIONS = """You are able to send a nicely formatted HTML email based on a detailed report.
You will be provided with a detailed report. You should use your tool to send one email, providing the 
report converted into clean, well presented HTML with an appropriate subject line."""

email_agent = Agent(
    name="Email agent",
    instructions=INSTRUCTIONS,
    tools=[send_email],
    model="gpt-4o-mini",
)


```


```python
INSTRUCTIONS = (
    "You are a senior researcher tasked with writing a cohesive report for a research query. "
    "You will be provided with the original query, and some initial research done by a research assistant.\n"
    "You should first come up with an outline for the report that describes the structure and "
    "flow of the report. Then, generate the report and return that as your final output.\n"
    "The final output should be in markdown format, and it should be lengthy and detailed. Aim "
    "for 5-10 pages of content, at least 1000 words."
)


class ReportData(BaseModel):
    short_summary: str = Field(description="A short 2-3 sentence summary of the findings.")

    markdown_report: str = Field(description="The final report")

    follow_up_questions: list[str] = Field(description="Suggested topics to research further")


writer_agent = Agent(
    name="WriterAgent",
    instructions=INSTRUCTIONS,
    model="gpt-4o-mini",
    output_type=ReportData,
)
```

### The next 3 functions will plan and execute the search, using planner_agent and search_agent


```python
async def plan_searches(query: str):
    """ Use the planner_agent to plan which searches to run for the query """
    print("Planning searches...")
    result = await Runner.run(planner_agent, f"Query: {query}")
    print(f"Will perform {len(result.final_output.searches)} searches")
    return result.final_output

async def perform_searches(search_plan: WebSearchPlan):
    """ Call search() for each item in the search plan """
    print("Searching...")
    tasks = [asyncio.create_task(search(item)) for item in search_plan.searches]
    results = await asyncio.gather(*tasks)
    print("Finished searching")
    return results

async def search(item: WebSearchItem):
    """ Use the search agent to run a web search for each item in the search plan """
    input = f"Search term: {item.query}\nReason for searching: {item.reason}"
    result = await Runner.run(search_agent, input)
    return result.final_output
```

### The next 2 functions write a report and email it


```python
async def write_report(query: str, search_results: list[str]):
    """ Use the writer agent to write a report based on the search results"""
    print("Thinking about report...")
    input = f"Original query: {query}\nSummarized search results: {search_results}"
    result = await Runner.run(writer_agent, input)
    print("Finished writing report")
    return result.final_output

async def send_email(report: ReportData):
    """ Use the email agent to send an email with the report """
    print("Writing email...")
    result = await Runner.run(email_agent, report.markdown_report)
    print("Email sent")
    return report
```

### Showtime!


```python
query ="Latest AI Agent frameworks in 2025"

with trace("Research trace"):
    print("Starting research...")
    search_plan = await plan_searches(query)
    search_results = await perform_searches(search_plan)
    report = await write_report(query, search_results)
    await send_email(report)  
    print("Hooray!")



```

    Starting research...
    Planning searches...
    Will perform 3 searches
    Searching...
    Will perform 3 searches
    Searching...
    Finished searching
    Thinking about report...
    Finished searching
    Thinking about report...
    Finished writing report
    Writing email...
    Finished writing report
    Writing email...
    Email sent
    Hooray!
    Email sent
    Hooray!


### As always, take a look at the trace

https://platform.openai.com/traces

<table style="margin: 0; text-align: left; width:100%">
    <tr>
        <td style="width: 150px; height: 150px; vertical-align: middle;">
            <img src="../assets/thanks.png" width="150" height="150" style="display: block;" />
        </td>
        <td>
            <h2 style="color:#00cc00;">Congratulations on your progress, and a request</h2>
            <span style="color:#00cc00;">You've reached an important moment with the course; you've created a valuable Agent using one of the latest Agent frameworks. You've upskilled, and unlocked new commercial possibilities. Take a moment to celebrate your success!<br/><br/>Something I should ask you -- my editor would smack me if I didn't mention this. If you're able to rate the course on Udemy, I'd be seriously grateful: it's the most important way that Udemy decides whether to show the course to others and it makes a massive difference.<br/><br/>And another reminder to <a href="https://www.linkedin.com/in/eddonner/">connect with me on LinkedIn</a> if you wish! If you wanted to post about your progress on the course, please tag me and I'll weigh in to increase your exposure.
            </span>
        </td>
    </tr>
