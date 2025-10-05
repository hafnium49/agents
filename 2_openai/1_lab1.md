## Week 2 Day 1

And now! Our first look at OpenAI Agents SDK

You won't believe how lightweight this is..

<table style="margin: 0; text-align: left; width:100%">
    <tr>
        <td style="width: 150px; height: 150px; vertical-align: middle;">
            <img src="../assets/tools.png" width="150" height="150" style="display: block;" />
        </td>
        <td>
            <h2 style="color:#00bfff;">The OpenAI Agents SDK Docs</h2>
            <span style="color:#00bfff;">The documentation on OpenAI Agents SDK is really clear and simple: <a href="https://openai.github.io/openai-agents-python/">https://openai.github.io/openai-agents-python/</a> and it's well worth a look.
            </span>
        </td>
    </tr>
</table>


```python
# The imports

from dotenv import load_dotenv
from agents import Agent, Runner, trace


```


```python
# The usual starting point

load_dotenv(override=True)

```




    True




```python

# Make an agent with name, instructions, model

agent = Agent(name="Jokester", instructions="You are a joke teller", model="gpt-4o-mini")
```


```python
agent
```




    Agent(name='Jokester', instructions='You are a joke teller', prompt=None, handoff_description=None, handoffs=[], model='gpt-4o-mini', model_settings=ModelSettings(temperature=None, top_p=None, frequency_penalty=None, presence_penalty=None, tool_choice=None, parallel_tool_calls=None, truncation=None, max_tokens=None, reasoning=None, metadata=None, store=None, include_usage=None, extra_query=None, extra_body=None, extra_headers=None, extra_args=None), tools=[], mcp_servers=[], mcp_config={}, input_guardrails=[], output_guardrails=[], output_type=None, hooks=None, tool_use_behavior='run_llm_again', reset_tool_choice=True)




```python
result = Runner.run(agent, "Tell a joke about Autonomous AI Agents")
print(result.final_output)
```


    ---------------------------------------------------------------------------

    AttributeError                            Traceback (most recent call last)

    Cell In[7], line 2
          1 result = Runner.run(agent, "Tell a joke about Autonomous AI Agents")
    ----> 2 print(result.final_output)


    AttributeError: 'coroutine' object has no attribute 'final_output'



```python
# Run the joke with Runner.run(agent, prompt) then print final_output

with trace("Telling a joke"):
    result = await Runner.run(agent, "Tell a joke about Autonomous AI Agents")
    print(result.final_output)
```

    Why don't autonomous AI agents ever play hide and seek?
    
    Because good luck hiding when they can track your every move!


## Now go and look at the trace

https://platform.openai.com/traces
