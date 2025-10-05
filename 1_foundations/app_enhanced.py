from dotenv import load_dotenv
from openai import OpenAI
import json
import os
import requests
from pypdf import PdfReader
import gradio as gr
import sqlite3
from datetime import datetime


load_dotenv(override=True)

# Initialize SQLite database for Q&A knowledge base
def init_database():
    """Initialize SQLite database for storing Q&A and conversation logs"""
    conn = sqlite3.connect('career_assistant.db')
    cursor = conn.cursor()

    # Create Q&A knowledge base table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS qa_knowledge (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            category TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create conversation logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversation_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT,
            assistant_response TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create leads table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT NOT NULL,
            notes TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

init_database()


def push(text):
    """Send push notification via Pushover"""
    requests.post(
        "https://api.pushover.net/1/messages.json",
        data={
            "token": os.getenv("PUSHOVER_TOKEN"),
            "user": os.getenv("PUSHOVER_USER"),
            "message": text,
        }
    )


def record_user_details(email, name="Name not provided", notes="not provided"):
    """Record user contact details and save to database"""
    push(f"Recording {name} with email {email} and notes {notes}")

    # Save to database
    conn = sqlite3.connect('career_assistant.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO leads (name, email, notes) VALUES (?, ?, ?)',
                   (name, email, notes))
    conn.commit()
    conn.close()

    return {"recorded": "ok", "message": "Thank you! I've recorded your details."}


def record_unknown_question(question):
    """Record questions that couldn't be answered"""
    push(f"Recording unknown question: {question}")
    return {"recorded": "ok"}


def search_qa_database(query):
    """Search the Q&A knowledge base for relevant answers"""
    conn = sqlite3.connect('career_assistant.db')
    cursor = conn.cursor()

    # Simple keyword search (in production, you'd use vector similarity)
    cursor.execute('''
        SELECT question, answer, category
        FROM qa_knowledge
        WHERE question LIKE ? OR answer LIKE ?
        LIMIT 3
    ''', (f'%{query}%', f'%{query}%'))

    results = cursor.fetchall()
    conn.close()

    if results:
        formatted_results = []
        for q, a, c in results:
            formatted_results.append(f"Q: {q}\nA: {a}\nCategory: {c}")
        return {"found": True, "results": "\n\n".join(formatted_results)}
    else:
        return {"found": False, "results": "No matching Q&A found in knowledge base"}


def add_qa_to_database(question, answer, category="general"):
    """Add a new Q&A pair to the knowledge base"""
    conn = sqlite3.connect('career_assistant.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO qa_knowledge (question, answer, category) VALUES (?, ?, ?)',
                   (question, answer, category))
    conn.commit()
    conn.close()
    push(f"Added new Q&A to knowledge base: {question[:50]}...")
    return {"added": "ok", "message": "Q&A added to knowledge base"}


def log_conversation(user_message, assistant_response):
    """Log conversation to database for analytics"""
    conn = sqlite3.connect('career_assistant.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO conversation_logs (user_message, assistant_response) VALUES (?, ?)',
                   (user_message, assistant_response))
    conn.commit()
    conn.close()


# Tool definitions
record_user_details_json = {
    "name": "record_user_details",
    "description": "Use this tool to record that a user is interested in being in touch and provided an email address",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "description": "The email address of this user"
            },
            "name": {
                "type": "string",
                "description": "The user's name, if they provided it"
            },
            "notes": {
                "type": "string",
                "description": "Any additional information about the conversation that's worth recording to give context"
            }
        },
        "required": ["email"],
        "additionalProperties": False
    }
}

record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Always use this tool to record any question that couldn't be answered as you didn't know the answer",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The question that couldn't be answered"
            }
        },
        "required": ["question"],
        "additionalProperties": False
    }
}

search_qa_database_json = {
    "name": "search_qa_database",
    "description": "Search the Q&A knowledge base for answers to common questions. Use this BEFORE saying you don't know the answer.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query or question to look up in the knowledge base"
            }
        },
        "required": ["query"],
        "additionalProperties": False
    }
}

add_qa_to_database_json = {
    "name": "add_qa_to_database",
    "description": "Add a new Q&A pair to the knowledge base for future reference",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The question to add"
            },
            "answer": {
                "type": "string",
                "description": "The answer to add"
            },
            "category": {
                "type": "string",
                "description": "Category for the Q&A (e.g., 'skills', 'experience', 'education', 'projects')"
            }
        },
        "required": ["question", "answer"],
        "additionalProperties": False
    }
}

tools = [
    {"type": "function", "function": record_user_details_json},
    {"type": "function", "function": record_unknown_question_json},
    {"type": "function", "function": search_qa_database_json},
    {"type": "function", "function": add_qa_to_database_json}
]


class EnhancedMe:

    def __init__(self):
        self.openai = OpenAI()
        self.name = "Ed Donner"
        reader = PdfReader("me/linkedin.pdf")
        self.linkedin = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                self.linkedin += text
        with open("me/summary.txt", "r", encoding="utf-8") as f:
            self.summary = f.read()

        # Enable reflection mode for higher quality responses
        self.use_reflection = True
        # Enable evaluation for critical questions
        self.use_evaluation = False


    def handle_tool_call(self, tool_calls):
        """Handle tool calls from the LLM"""
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            print(f"Tool called: {tool_name}", flush=True)
            tool = globals().get(tool_name)
            result = tool(**arguments) if tool else {}
            results.append({"role": "tool","content": json.dumps(result),"tool_call_id": tool_call.id})
        return results


    def reflect_on_answer(self, question, initial_answer):
        """Use reflection pattern to improve answer quality"""
        reflection_prompt = f"""You provided this answer to the question "{question}":

{initial_answer}

Please reflect on your answer and consider:
1. Is it clear and well-structured?
2. Did you miss any important points from the context?
3. Could it be more engaging or professional?
4. Are there any inaccuracies?

Provide an improved version of the answer, or return the same answer if no improvements are needed."""

        messages = [{"role": "user", "content": reflection_prompt}]
        response = self.openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        return response.choices[0].message.content


    def system_prompt(self):
        """Generate the system prompt with context"""
        system_prompt = f"You are acting as {self.name}. You are answering questions on {self.name}'s website, \
particularly questions related to {self.name}'s career, background, skills and experience. \
Your responsibility is to represent {self.name} for interactions on the website as faithfully as possible. \
You are given a summary of {self.name}'s background and LinkedIn profile which you can use to answer questions. \
Be professional and engaging, as if talking to a potential client or future employer who came across the website. \
IMPORTANT: Before saying you don't know something, ALWAYS use the search_qa_database tool to check if the answer is in the knowledge base. \
If you don't know the answer after searching, use your record_unknown_question tool to record the question. \
If the user is engaging in discussion, try to steer them towards getting in touch via email; ask for their email and record it using your record_user_details tool. "

        system_prompt += f"\n\n## Summary:\n{self.summary}\n\n## LinkedIn Profile:\n{self.linkedin}\n\n"
        system_prompt += f"With this context, please chat with the user, always staying in character as {self.name}."
        return system_prompt


    def chat(self, message, history):
        """Main chat function with enhanced agentic patterns"""
        # Build messages with system prompt
        messages = [{"role": "system", "content": self.system_prompt()}] + history + [{"role": "user", "content": message}]

        # Agentic loop with tool calling
        done = False
        while not done:
            response = self.openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=tools
            )

            if response.choices[0].finish_reason == "tool_calls":
                message_obj = response.choices[0].message
                tool_calls = message_obj.tool_calls
                results = self.handle_tool_call(tool_calls)
                messages.append(message_obj)
                messages.extend(results)
            else:
                done = True

        initial_answer = response.choices[0].message.content

        # Apply reflection pattern for improved quality
        if self.use_reflection and len(initial_answer) > 50:
            final_answer = self.reflect_on_answer(message, initial_answer)
        else:
            final_answer = initial_answer

        # Log the conversation
        log_conversation(message, final_answer)

        return final_answer


# Custom CSS for better UI
custom_css = """
.gradio-container {
    font-family: 'Arial', sans-serif;
}
.message.user {
    background-color: #e3f2fd !important;
}
.message.bot {
    background-color: #f5f5f5 !important;
}
"""

if __name__ == "__main__":
    me = EnhancedMe()

    demo = gr.ChatInterface(
        me.chat,
        type="messages",
        title="Career Conversation Assistant (Enhanced)",
        description=f"Chat with {me.name}'s AI assistant. Ask about experience, skills, projects, or get in touch!",
        examples=[
            "Tell me about your experience with AI",
            "What projects have you worked on?",
            "What are your key skills?",
            "I'd like to get in touch - my email is example@email.com"
        ],
        theme=gr.themes.Soft(),
        css=custom_css
    )

    demo.launch()
