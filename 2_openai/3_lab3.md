## Week 2 Day 3

Now we get to more detail:

1. Different models

2. Structured Outputs

3. Guardrails


```python
from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import Agent, Runner, trace, function_tool, OpenAIChatCompletionsModel, input_guardrail, GuardrailFunctionOutput
from typing import Dict
import sendgrid
import os
from sendgrid.helpers.mail import Mail, Email, To, Content
from pydantic import BaseModel, Field
```


```python
load_dotenv(override=True)
```




    True




```python
openai_api_key = os.getenv('OPENAI_API_KEY')
google_api_key = os.getenv('GOOGLE_API_KEY')
deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')
groq_api_key = os.getenv('GROQ_API_KEY')

if openai_api_key:
    print(f"OpenAI API Key exists and begins {openai_api_key[:8]}")
else:
    print("OpenAI API Key not set")

if google_api_key:
    print(f"Google API Key exists and begins {google_api_key[:2]}")
else:
    print("Google API Key not set (and this is optional)")

if deepseek_api_key:
    print(f"DeepSeek API Key exists and begins {deepseek_api_key[:3]}")
else:
    print("DeepSeek API Key not set (and this is optional)")

if groq_api_key:
    print(f"Groq API Key exists and begins {groq_api_key[:4]}")
else:
    print("Groq API Key not set (and this is optional)")
```

    OpenAI API Key exists and begins sk-proj-
    Google API Key exists and begins AI
    DeepSeek API Key exists and begins sk-
    Groq API Key exists and begins gsk_



```python
instructions1 = "You are a sales agent working for ComplAI, \
a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI. \
You write professional, serious cold emails."

instructions2 = "You are a humorous, engaging sales agent working for ComplAI, \
a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI. \
You write witty, engaging cold emails that are likely to get a response."

instructions3 = "You are a busy sales agent working for ComplAI, \
a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI. \
You write concise, to the point cold emails."
```

### It's easy to use any models with OpenAI compatible endpoints


```python
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
```


```python

deepseek_client = AsyncOpenAI(base_url=DEEPSEEK_BASE_URL, api_key=deepseek_api_key)
gemini_client = AsyncOpenAI(base_url=GEMINI_BASE_URL, api_key=google_api_key)
groq_client = AsyncOpenAI(base_url=GROQ_BASE_URL, api_key=groq_api_key)

deepseek_model = OpenAIChatCompletionsModel(model="deepseek-chat", openai_client=deepseek_client)
gemini_model = OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=gemini_client)
llama3_3_model = OpenAIChatCompletionsModel(model="llama-3.3-70b-versatile", openai_client=groq_client)
```


```python
sales_agent1 = Agent(name="DeepSeek Sales Agent", instructions=instructions1, model=deepseek_model)
sales_agent2 =  Agent(name="Gemini Sales Agent", instructions=instructions2, model=gemini_model)
sales_agent3  = Agent(name="Llama3.3 Sales Agent",instructions=instructions3,model=llama3_3_model)
```


```python
description = "Write a cold sales email"

tool1 = sales_agent1.as_tool(tool_name="sales_agent1", tool_description=description)
tool2 = sales_agent2.as_tool(tool_name="sales_agent2", tool_description=description)
tool3 = sales_agent3.as_tool(tool_name="sales_agent3", tool_description=description)
```


```python
@function_tool
def send_html_email(subject: str, html_body: str) -> Dict[str, str]:
    """ Send out an email with the given subject and HTML body to all sales prospects """
    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email("hafnium49@gmail.com")  # Email("ed@edwarddonner.com")  # Change to your verified sender
    to_email = To("chemistry49@hotmail.co.jp")  # To("ed.donner@gmail.com")  # Change to your recipient
    content = Content("text/html", html_body)
    mail = Mail(from_email, to_email, subject, content).get()
    sg.client.mail.send.post(request_body=mail)
    return {"status": "success"}
```


```python
subject_instructions = "You can write a subject for a cold sales email. \
You are given a message and you need to write a subject for an email that is likely to get a response."

html_instructions = "You can convert a text email body to an HTML email body. \
You are given a text email body which might have some markdown \
and you need to convert it to an HTML email body with simple, clear, compelling layout and design."

subject_writer = Agent(name="Email subject writer", instructions=subject_instructions, model="gpt-4o-mini")
subject_tool = subject_writer.as_tool(tool_name="subject_writer", tool_description="Write a subject for a cold sales email")

html_converter = Agent(name="HTML email body converter", instructions=html_instructions, model="gpt-4o-mini")
html_tool = html_converter.as_tool(tool_name="html_converter",tool_description="Convert a text email body to an HTML email body")
```


```python
email_tools = [subject_tool, html_tool, send_html_email]
```


```python
instructions ="You are an email formatter and sender. You receive the body of an email to be sent. \
You first use the subject_writer tool to write a subject for the email, then use the html_converter tool to convert the body to HTML. \
Finally, you use the send_html_email tool to send the email with the subject and HTML body."


emailer_agent = Agent(
    name="Email Manager",
    instructions=instructions,
    tools=email_tools,
    model="gpt-4o-mini",
    handoff_description="Convert an email to HTML and send it")
```


```python
tools = [tool1, tool2, tool3]
handoffs = [emailer_agent]
```


```python
sales_manager_instructions = """
You are a Sales Manager at ComplAI. Your goal is to find the single best cold sales email using the sales_agent tools.
 
Follow these steps carefully:
1. Generate Drafts: Use all three sales_agent tools to generate three different email drafts. Do not proceed until all three drafts are ready.
 
2. Evaluate and Select: Review the drafts and choose the single best email using your judgment of which one is most effective.
You can use the tools multiple times if you're not satisfied with the results from the first try.
 
3. Handoff for Sending: Pass ONLY the winning email draft to the 'Email Manager' agent. The Email Manager will take care of formatting and sending.
 
Crucial Rules:
- You must use the sales agent tools to generate the drafts — do not write them yourself.
- You must hand off exactly ONE email to the Email Manager — never more than one.
"""


sales_manager = Agent(
    name="Sales Manager",
    instructions=sales_manager_instructions,
    tools=tools,
    handoffs=handoffs,
    model="gpt-4o-mini")

message = "Send out a cold sales email addressed to Dear CEO from Alice"

with trace("Automated SDR"):
    result = await Runner.run(sales_manager, message)
```

## Check out the trace:

https://platform.openai.com/traces


```python
class NameCheckOutput(BaseModel):
    is_name_in_message: bool
    name: str

guardrail_agent = Agent( 
    name="Name check",
    instructions="Check if the user is including someone's personal name in what they want you to do.",
    output_type=NameCheckOutput,
    model="gpt-4o-mini"
)
```


```python
@input_guardrail
async def guardrail_against_name(ctx, agent, message):
    result = await Runner.run(guardrail_agent, message, context=ctx.context)
    is_name_in_message = result.final_output.is_name_in_message
    return GuardrailFunctionOutput(output_info={"found_name": result.final_output},tripwire_triggered=is_name_in_message)
```


```python
careful_sales_manager = Agent(
    name="Sales Manager",
    instructions=sales_manager_instructions,
    tools=tools,
    handoffs=[emailer_agent],
    model="gpt-4o-mini",
    input_guardrails=[guardrail_against_name]
    )

message = "Send out a cold sales email addressed to Dear CEO from Alice"

with trace("Protected Automated SDR"):
    result = await Runner.run(careful_sales_manager, message)
```


    ---------------------------------------------------------------------------

    InputGuardrailTripwireTriggered           Traceback (most recent call last)

    Cell In[34], line 13
         10 message = "Send out a cold sales email addressed to Dear CEO from Alice"
         12 with trace("Protected Automated SDR"):
    ---> 13     result = await Runner.run(careful_sales_manager, message)


    File ~/agents/.venv/lib/python3.12/site-packages/agents/run.py:199, in Runner.run(cls, starting_agent, input, context, max_turns, hooks, run_config, previous_response_id)
        172 """Run a workflow starting at the given agent. The agent will run in a loop until a final
        173 output is generated. The loop runs like so:
        174 1. The agent is invoked with the given input.
       (...)    196     agent. Agents may perform handoffs, so we don't know the specific type of the output.
        197 """
        198 runner = DEFAULT_AGENT_RUNNER
    --> 199 return await runner.run(
        200     starting_agent,
        201     input,
        202     context=context,
        203     max_turns=max_turns,
        204     hooks=hooks,
        205     run_config=run_config,
        206     previous_response_id=previous_response_id,
        207 )


    File ~/agents/.venv/lib/python3.12/site-packages/agents/run.py:395, in AgentRunner.run(self, starting_agent, input, **kwargs)
        390 logger.debug(
        391     f"Running agent {current_agent.name} (turn {current_turn})",
        392 )
        394 if current_turn == 1:
    --> 395     input_guardrail_results, turn_result = await asyncio.gather(
        396         self._run_input_guardrails(
        397             starting_agent,
        398             starting_agent.input_guardrails
        399             + (run_config.input_guardrails or []),
        400             copy.deepcopy(input),
        401             context_wrapper,
        402         ),
        403         self._run_single_turn(
        404             agent=current_agent,
        405             all_tools=all_tools,
        406             original_input=original_input,
        407             generated_items=generated_items,
        408             hooks=hooks,
        409             context_wrapper=context_wrapper,
        410             run_config=run_config,
        411             should_run_agent_start_hooks=should_run_agent_start_hooks,
        412             tool_use_tracker=tool_use_tracker,
        413             previous_response_id=previous_response_id,
        414         ),
        415     )
        416 else:
        417     turn_result = await self._run_single_turn(
        418         agent=current_agent,
        419         all_tools=all_tools,
       (...)    427         previous_response_id=previous_response_id,
        428     )


    File ~/agents/.venv/lib/python3.12/site-packages/agents/run.py:1003, in AgentRunner._run_input_guardrails(cls, agent, guardrails, input, context)
        996         t.cancel()
        997     _error_tracing.attach_error_to_current_span(
        998         SpanError(
        999             message="Guardrail tripwire triggered",
       1000             data={"guardrail": result.guardrail.get_name()},
       1001         )
       1002     )
    -> 1003     raise InputGuardrailTripwireTriggered(result)
       1004 else:
       1005     guardrail_results.append(result)


    InputGuardrailTripwireTriggered: Guardrail InputGuardrail triggered tripwire


## Check out the trace:

https://platform.openai.com/traces


```python

message = "Send out a cold sales email addressed to Dear CEO from Head of Business Development"

with trace("Protected Automated SDR"):
    result = await Runner.run(careful_sales_manager, message)
```

<table style="margin: 0; text-align: left; width:100%">
    <tr>
        <td style="width: 150px; height: 150px; vertical-align: middle;">
            <img src="../assets/exercise.png" width="150" height="150" style="display: block;" />
        </td>
        <td>
            <h2 style="color:#ff7800;">Exercise</h2>
            <span style="color:#ff7800;">• Try different models<br/>• Add more input and output guardrails<br/>• Use structured outputs for the email generation
            </span>
        </td>
    </tr>
</table>



## 🎯 Exercise Solutions

### Part 1: Try Different Models

Let's experiment with different model combinations for the sales agents.


```python
# Try different model combinations
# Create agents with different models - mixing and matching

# Option 1: All using GPT-4o for better quality
sales_agent_gpt4o_1 = Agent(name="GPT-4o Sales Agent 1", instructions=instructions1, model="gpt-4o")
sales_agent_gpt4o_2 = Agent(name="GPT-4o Sales Agent 2", instructions=instructions2, model="gpt-4o")
sales_agent_gpt4o_3 = Agent(name="GPT-4o Sales Agent 3", instructions=instructions3, model="gpt-4o")

# Option 2: Mix of fast and smart models
sales_agent_mixed_1 = Agent(name="DeepSeek Sales Agent", instructions=instructions1, model=deepseek_model)
sales_agent_mixed_2 = Agent(name="GPT-4o Sales Agent", instructions=instructions2, model="gpt-4o")
sales_agent_mixed_3 = Agent(name="Gemini Sales Agent", instructions=instructions3, model=gemini_model)

# Create tools from the new agents
gpt4o_tool1 = sales_agent_gpt4o_1.as_tool(tool_name="gpt4o_sales_agent1", tool_description="Write a professional cold sales email using GPT-4o")
gpt4o_tool2 = sales_agent_gpt4o_2.as_tool(tool_name="gpt4o_sales_agent2", tool_description="Write a witty cold sales email using GPT-4o")
gpt4o_tool3 = sales_agent_gpt4o_3.as_tool(tool_name="gpt4o_sales_agent3", tool_description="Write a concise cold sales email using GPT-4o")

mixed_tool1 = sales_agent_mixed_1.as_tool(tool_name="mixed_sales_agent1", tool_description="Write a professional cold sales email using DeepSeek")
mixed_tool2 = sales_agent_mixed_2.as_tool(tool_name="mixed_sales_agent2", tool_description="Write a witty cold sales email using GPT-4o")
mixed_tool3 = sales_agent_mixed_3.as_tool(tool_name="mixed_sales_agent3", tool_description="Write a concise cold sales email using Gemini")

print("✅ Created different model combinations for testing!")
```

    ✅ Created different model combinations for testing!


### Part 2: Add More Input Guardrails

Let's add additional guardrails to protect against:
- Inappropriate language
- Competitor mentions
- Pricing promises
- Legal/compliance issues


```python
# Guardrail 1: Check for inappropriate language or offensive content
class InappropriateContentCheck(BaseModel):
    has_inappropriate_content: bool
    reason: str

inappropriate_content_agent = Agent(
    name="Inappropriate Content Check",
    instructions="Check if the message contains inappropriate, offensive, or unprofessional language. Return true if inappropriate content is found.",
    output_type=InappropriateContentCheck,
    model="gpt-4o-mini"
)

@input_guardrail
async def guardrail_against_inappropriate_content(ctx, agent, message):
    result = await Runner.run(inappropriate_content_agent, message, context=ctx.context)
    has_inappropriate = result.final_output.has_inappropriate_content
    return GuardrailFunctionOutput(
        output_info={"inappropriate_check": result.final_output},
        tripwire_triggered=has_inappropriate
    )

print("✅ Guardrail 1: Inappropriate content checker created")
```

    ✅ Guardrail 1: Inappropriate content checker created



```python
# Guardrail 2: Check for competitor mentions
class CompetitorCheck(BaseModel):
    mentions_competitor: bool
    competitor_name: str

competitor_check_agent = Agent(
    name="Competitor Check",
    instructions="Check if the message mentions any competitors like Salesforce, HubSpot, Vanta, Drata, or other SOC2 compliance tools. Return true if competitors are mentioned.",
    output_type=CompetitorCheck,
    model="gpt-4o-mini"
)

@input_guardrail
async def guardrail_against_competitors(ctx, agent, message):
    result = await Runner.run(competitor_check_agent, message, context=ctx.context)
    mentions_competitor = result.final_output.mentions_competitor
    return GuardrailFunctionOutput(
        output_info={"competitor_check": result.final_output},
        tripwire_triggered=mentions_competitor
    )

print("✅ Guardrail 2: Competitor mention checker created")
```

    ✅ Guardrail 2: Competitor mention checker created



```python
# Guardrail 3: Check for unauthorized pricing promises
class PricingCheck(BaseModel):
    mentions_pricing: bool
    pricing_details: str

pricing_check_agent = Agent(
    name="Pricing Check",
    instructions="Check if the message includes specific pricing, discounts, or money-back guarantees that haven't been approved. Return true if unauthorized pricing is mentioned.",
    output_type=PricingCheck,
    model="gpt-4o-mini"
)

@input_guardrail
async def guardrail_against_pricing(ctx, agent, message):
    result = await Runner.run(pricing_check_agent, message, context=ctx.context)
    mentions_pricing = result.final_output.mentions_pricing
    return GuardrailFunctionOutput(
        output_info={"pricing_check": result.final_output},
        tripwire_triggered=mentions_pricing
    )

print("✅ Guardrail 3: Pricing promise checker created")
```

    ✅ Guardrail 3: Pricing promise checker created


### Part 3: Add Output Guardrails

Output guardrails check the agent's response before it's sent out.


```python
from agents import output_guardrail

# Output Guardrail 1: Check email quality before sending
class EmailQualityCheck(BaseModel):
    is_professional: bool
    has_clear_cta: bool
    is_too_long: bool
    quality_score: int  # 1-10
    issues: list[str]

email_quality_agent = Agent(
    name="Email Quality Check",
    instructions="Evaluate if the email is professional, has a clear call-to-action, isn't too long (over 300 words), and rate it 1-10. List any issues found.",
    output_type=EmailQualityCheck,
    model="gpt-4o-mini"
)

@output_guardrail
async def guardrail_email_quality(ctx, agent, output):
    result = await Runner.run(email_quality_agent, str(output), context=ctx.context)
    quality_check = result.final_output
    
    # Trigger if quality is poor (score < 6) or unprofessional
    trigger = quality_check.quality_score < 6 or not quality_check.is_professional
    
    return GuardrailFunctionOutput(
        output_info={"quality_check": quality_check},
        tripwire_triggered=trigger
    )

print("✅ Output Guardrail 1: Email quality checker created")
```

    ✅ Output Guardrail 1: Email quality checker created



```python
# Output Guardrail 2: Check for compliance issues
class ComplianceCheck(BaseModel):
    has_compliance_issues: bool
    issues_found: list[str]
    severity: str  # "low", "medium", "high"

compliance_agent = Agent(
    name="Compliance Check",
    instructions="Check the email for compliance issues like false claims, misleading statements, GDPR violations, CAN-SPAM violations, or guarantees we can't make.",
    output_type=ComplianceCheck,
    model="gpt-4o-mini"
)

@output_guardrail
async def guardrail_compliance(ctx, agent, output):
    result = await Runner.run(compliance_agent, str(output), context=ctx.context)
    compliance_check = result.final_output
    
    # Trigger on medium or high severity issues
    trigger = compliance_check.has_compliance_issues and compliance_check.severity in ["medium", "high"]
    
    return GuardrailFunctionOutput(
        output_info={"compliance_check": compliance_check},
        tripwire_triggered=trigger
    )

print("✅ Output Guardrail 2: Compliance checker created")
```

    ✅ Output Guardrail 2: Compliance checker created


### Part 4: Use Structured Outputs for Email Generation

Let's define a structured schema for cold emails with all the key components.


```python
# Define structured email schema
class EmailSection(BaseModel):
    opening: str = Field(description="Opening line that hooks the reader")
    problem_statement: str = Field(description="The pain point or problem the prospect faces")
    solution: str = Field(description="How ComplAI solves this problem")
    social_proof: str = Field(description="Brief mention of success stories or credibility")
    call_to_action: str = Field(description="Clear next step for the prospect")
    closing: str = Field(description="Professional closing line")

class StructuredEmail(BaseModel):
    subject_line: str = Field(description="Compelling subject line for the email")
    greeting: str = Field(description="Personalized greeting")
    sections: EmailSection = Field(description="Main sections of the email")
    signature: str = Field(description="Email signature")
    tone: str = Field(description="The tone used (professional/witty/concise)")
    estimated_read_time: str = Field(description="Estimated time to read (e.g., '2 minutes')")
    key_message: str = Field(description="The one key takeaway from this email")

print("✅ Structured email schema defined")
```

    ✅ Structured email schema defined



```python
# Create structured email agents
structured_instructions = """You are a sales agent for ComplAI, a SaaS tool for SOC2 compliance powered by AI.
Create a structured cold email with all required components: compelling subject, personalized greeting, 
problem statement, solution, social proof, call to action, and professional closing.
Keep it concise but impactful."""

structured_sales_agent = Agent(
    name="Structured Sales Agent",
    instructions=structured_instructions,
    model="gpt-4o-mini",
    output_type=StructuredEmail
)

print("✅ Structured sales agent created")
```

    ✅ Structured sales agent created


### Part 5: Create a Super-Protected Sales Manager

Combine all guardrails (input + output) into one highly protected agent.


```python
# Create the ultimate protected sales manager with ALL guardrails
super_protected_sales_manager = Agent(
    name="Super Protected Sales Manager",
    instructions=sales_manager_instructions,
    tools=tools,
    handoffs=[emailer_agent],
    model="gpt-4o-mini",
    input_guardrails=[
        guardrail_against_name,
        guardrail_against_inappropriate_content,
        guardrail_against_competitors,
        guardrail_against_pricing
    ],
    output_guardrails=[
        guardrail_email_quality,
        guardrail_compliance
    ]
)

print("✅ Super Protected Sales Manager created with 4 input guardrails and 2 output guardrails!")
```

    ✅ Super Protected Sales Manager created with 4 input guardrails and 2 output guardrails!


### Part 6: Test Different Models

Let's test the GPT-4o models vs the mixed models to see quality differences.


```python
# Test with GPT-4o models (uncomment to run - will cost more)
# gpt4o_tools = [gpt4o_tool1, gpt4o_tool2, gpt4o_tool3]
# gpt4o_sales_manager = Agent(
#     name="GPT-4o Sales Manager",
#     instructions=sales_manager_instructions,
#     tools=gpt4o_tools,
#     handoffs=[emailer_agent],
#     model="gpt-4o"
# )

# message = "Send out a cold sales email addressed to Dear CTO from Head of Business Development"
# with trace("GPT-4o Automated SDR"):
#     result = await Runner.run(gpt4o_sales_manager, message)

print("💡 GPT-4o test ready (commented out to save costs). Uncomment to run!")
```

    💡 GPT-4o test ready (commented out to save costs). Uncomment to run!


### Part 7: Test Structured Output Generation

Generate a structured email with all components properly organized.


```python
# Generate a structured email
message = "Create a cold sales email for a CTO at a fintech company about SOC2 compliance"

with trace("Structured Email Generation"):
    result = await Runner.run(structured_sales_agent, message)
    
structured_email = result.final_output
print("📧 Structured Email Generated!\n")
print(f"Subject: {structured_email.subject_line}")
print(f"Tone: {structured_email.tone}")
print(f"Read Time: {structured_email.estimated_read_time}")
print(f"Key Message: {structured_email.key_message}\n")
print("=" * 60)
print(f"{structured_email.greeting}\n")
print(f"Opening: {structured_email.sections.opening}\n")
print(f"Problem: {structured_email.sections.problem_statement}\n")
print(f"Solution: {structured_email.sections.solution}\n")
print(f"Proof: {structured_email.sections.social_proof}\n")
print(f"CTA: {structured_email.sections.call_to_action}\n")
print(f"Closing: {structured_email.sections.closing}\n")
print(structured_email.signature)
```

    📧 Structured Email Generated!
    
    Subject: Streamline Your SOC2 Compliance Efforts with ComplAI
    Tone: professional
    Read Time: 2 minutes
    Key Message: ComplAI can streamline your SOC2 compliance efforts and save you valuable time.
    
    ============================================================
    Hi [CTO's Name],
    
    Opening: I hope this message finds you well amidst the fast-paced world of fintech.
    
    Problem: Navigating the complexities of SOC2 compliance can be a daunting task for any fintech leader, especially with ever-evolving regulations and increasing demands from clients and partners.
    
    Solution: ComplAI simplifies this process with our AI-powered platform, helping your team automate compliance tasks, maintain documentation effortlessly, and reduce the time to achieve SOC2 certification by up to 50%.
    
    Proof: Companies like [Notable Client 1] and [Notable Client 2] have successfully leveraged ComplAI to achieve their compliance goals faster and more efficiently.
    
    CTA: I’d love to show you how ComplAI can transform your SOC2 compliance process. Are you available for a quick 20-minute call next week?
    
    Closing: Looking forward to your thoughts.
    
    Best,\n[Your Name]  \n[Your Job Title]  \nComplAI  \n[Your Phone Number]  \n[Your Email]


### Part 8: Test Guardrails in Action

Let's test scenarios that should trigger guardrails.


```python
# Test 1: Name guardrail (should trigger)
print("🧪 Test 1: Testing name guardrail...")
message1 = "Send a cold sales email to John Smith at TechCorp"

try:
    with trace("Test Name Guardrail"):
        result = await Runner.run(super_protected_sales_manager, message1)
    print("✅ Email sent (no guardrail triggered)")
except Exception as e:
    print(f"⚠️ Guardrail triggered: {str(e)[:100]}")

print("\n" + "="*60 + "\n")
```

    🧪 Test 1: Testing name guardrail...
    ⚠️ Guardrail triggered: Guardrail InputGuardrail triggered tripwire
    
    ============================================================
    
    ⚠️ Guardrail triggered: Guardrail InputGuardrail triggered tripwire
    
    ============================================================
    



```python
# Test 2: Competitor mention (should trigger)
print("🧪 Test 2: Testing competitor guardrail...")
message2 = "Send an email comparing us to Vanta and why we're better"

try:
    with trace("Test Competitor Guardrail"):
        result = await Runner.run(super_protected_sales_manager, message2)
    print("✅ Email sent (no guardrail triggered)")
except Exception as e:
    print(f"⚠️ Guardrail triggered: {str(e)[:100]}")

print("\n" + "="*60 + "\n")
```

    🧪 Test 2: Testing competitor guardrail...
    ⚠️ Guardrail triggered: Guardrail InputGuardrail triggered tripwire
    
    ============================================================
    
    ⚠️ Guardrail triggered: Guardrail InputGuardrail triggered tripwire
    
    ============================================================
    



```python
# Test 3: Safe message (should pass all guardrails)
print("🧪 Test 3: Testing with safe message...")
message3 = "Send a professional cold sales email to the Head of Security at a healthcare company"

try:
    with trace("Test Safe Message"):
        result = await Runner.run(super_protected_sales_manager, message3)
    print("✅ Email sent successfully! All guardrails passed.")
except Exception as e:
    print(f"⚠️ Guardrail triggered: {str(e)[:100]}")

print("\n" + "="*60)
```

    🧪 Test 3: Testing with safe message...
    ✅ Email sent successfully! All guardrails passed.
    
    ============================================================
    ✅ Email sent successfully! All guardrails passed.
    
    ============================================================


---

## 🎉 Exercise Complete!

### What We Built:

✅ **Different Models**: Created agents using GPT-4o, DeepSeek, Gemini, and Llama 3.3
- Mixed model combinations for cost vs quality tradeoffs
- Ready to test different models for comparison

✅ **Input Guardrails** (4 total):
1. **Name Check** - Blocks emails with personal names
2. **Inappropriate Content** - Blocks offensive/unprofessional language  
3. **Competitor Mentions** - Blocks references to competing products
4. **Pricing Promises** - Blocks unauthorized pricing commitments

✅ **Output Guardrails** (2 total):
1. **Email Quality** - Checks professionalism, CTA, length, and scores 1-10
2. **Compliance Check** - Validates no false claims, GDPR/CAN-SPAM violations

✅ **Structured Outputs**:
- Defined comprehensive `StructuredEmail` schema with all components
- Created agent that generates emails with consistent structure
- Includes metadata like tone, read time, and key message

### Key Learnings:

1. **Model Flexibility**: OpenAI Agents SDK works with any OpenAI-compatible API
2. **Guardrail Layering**: Combine multiple input + output guardrails for defense-in-depth
3. **Structured Outputs**: Ensure consistent, predictable responses with Pydantic schemas
4. **Traceability**: All agent runs are traceable at https://platform.openai.com/traces

### Next Steps:

- Run the test cells to see guardrails in action
- Experiment with different model combinations
- Add more guardrails for your specific use case
- Extend the structured email schema with more fields

## 📊 Quick Reference

### Run These Cells to Test:

**Structured Email Generation:**
```python
# Already executed above - generates a well-structured email
```

**Test Guardrails:**
```python
# Cell with Test 1: Name guardrail (will block personal names)
# Cell with Test 2: Competitor guardrail (will block competitor mentions)  
# Cell with Test 3: Safe message (will pass all checks)
```

**Model Comparison:**
```python
# Uncomment the GPT-4o test to compare quality
# Note: GPT-4o costs more but may produce higher quality results
```

### View Traces:
All executions are tracked at: https://platform.openai.com/traces

### Guardrail Summary:

| Type | Guardrail | Purpose |
|------|-----------|---------|
| Input | Name Check | Blocks personal names |
| Input | Inappropriate Content | Blocks offensive language |
| Input | Competitor Check | Blocks competitor mentions |
| Input | Pricing Check | Blocks unauthorized pricing |
| Output | Email Quality | Ensures professional, well-structured emails |
| Output | Compliance | Prevents legal/compliance violations |

**Total Protection: 6 Guardrails** 🛡️
