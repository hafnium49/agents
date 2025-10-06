#!/usr/bin/env python3
"""
SendGrid Webhook Server for Automated Email Reply Handling

This server receives inbound emails via SendGrid's Inbound Parse webhook,
processes them through an AI agent, and sends automated contextual replies.

Setup Instructions:
1. Run: uv pip install flask python-dotenv sendgrid openai-agents
2. Expose this server using ngrok or similar: ngrok http 5000
3. Configure SendGrid Inbound Parse to point to: https://your-ngrok-url/webhook/inbound
4. Run this server: uv run python webhook_server.py
"""

from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import sqlite3
from datetime import datetime
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
from agents import Agent, Runner
import asyncio
import re

load_dotenv(override=True)

app = Flask(__name__)

# Initialize the reply handler agent
reply_handler_instructions = """
You are a professional sales development representative (SDR) for ComplAI, handling replies to cold outreach emails.

Your responsibilities:
1. Analyze the recipient's reply sentiment and intent
2. Provide helpful, contextual responses based on the conversation history
3. Address questions about SOC2 compliance, audits, and ComplAI's AI-powered solution
4. Move the conversation forward toward scheduling a demo or call
5. Be professional, concise, and helpful

Key points about ComplAI:
- AI-powered SaaS tool for SOC2 compliance and audit preparation
- Automates compliance workflows and documentation
- Reduces audit preparation time by 70%
- Provides real-time compliance monitoring

When responding:
- Reference previous conversation context
- Answer their specific questions
- Include a clear call-to-action
- Keep responses under 150 words
- Be personable but professional
"""

reply_handler_agent = Agent(
    name="Email Reply Handler",
    instructions=reply_handler_instructions,
    model="gpt-4o-mini"
)


def get_conversation_history(sender_email: str) -> list:
    """Retrieve conversation history based on sender email"""
    conn = sqlite3.connect('email_conversations.db')
    cursor = conn.cursor()
    
    # Find thread by recipient email
    cursor.execute('''
        SELECT m.direction, m.sender, m.recipient, m.subject, m.body, m.timestamp, m.thread_id
        FROM messages m
        JOIN conversations c ON m.thread_id = c.thread_id
        WHERE c.recipient_email = ?
        ORDER BY m.timestamp ASC
    ''', (sender_email,))
    
    messages = cursor.fetchall()
    conn.close()
    
    if not messages:
        return [], None
    
    thread_id = messages[0][6]
    
    return [
        {
            "direction": msg[0],
            "sender": msg[1],
            "recipient": msg[2],
            "subject": msg[3],
            "body": msg[4],
            "timestamp": msg[5]
        }
        for msg in messages
    ], thread_id


def save_inbound_email(thread_id: str, sender_email: str, subject: str, body: str):
    """Save an inbound email reply"""
    conn = sqlite3.connect('email_conversations.db')
    cursor = conn.cursor()
    
    timestamp = datetime.now().isoformat()
    
    cursor.execute('''
        UPDATE conversations 
        SET last_updated = ?, status = 'replied'
        WHERE thread_id = ?
    ''', (timestamp, thread_id))
    
    cursor.execute('''
        INSERT INTO messages (thread_id, direction, sender, recipient, subject, body, timestamp)
        VALUES (?, 'inbound', ?, 'us', ?, ?, ?)
    ''', (thread_id, sender_email, subject, body, timestamp))
    
    conn.commit()
    conn.close()


def save_outbound_reply(thread_id: str, recipient_email: str, subject: str, body: str):
    """Save an outbound reply"""
    conn = sqlite3.connect('email_conversations.db')
    cursor = conn.cursor()
    
    timestamp = datetime.now().isoformat()
    
    cursor.execute('''
        UPDATE conversations 
        SET last_updated = ?, status = 'active'
        WHERE thread_id = ?
    ''', (timestamp, thread_id))
    
    cursor.execute('''
        INSERT INTO messages (thread_id, direction, sender, recipient, subject, body, timestamp)
        VALUES (?, 'outbound', 'us', ?, ?, ?, ?)
    ''', (thread_id, recipient_email, subject, body, timestamp))
    
    conn.commit()
    conn.close()


async def generate_and_send_reply(sender_email: str, sender_name: str, inbound_body: str, original_subject: str):
    """Generate AI reply and send it"""
    
    # Get conversation history
    history, thread_id = get_conversation_history(sender_email)
    
    if not thread_id:
        print(f"⚠️  No conversation found for {sender_email}")
        return
    
    # Format conversation for the agent
    conversation_context = "CONVERSATION HISTORY:\n\n"
    for msg in history:
        direction_label = "US" if msg["direction"] == "outbound" else "THEM"
        conversation_context += f"[{direction_label}] {msg['body']}\n\n"
    
    conversation_context += f"[THEM - NEW REPLY] {inbound_body}\n\n"
    conversation_context += "Please generate a professional response that continues this conversation."
    
    # Generate reply using the agent
    print(f"🤖 Generating AI reply for thread {thread_id}...")
    result = await Runner.run(reply_handler_agent, conversation_context)
    reply_body = result.final_output
    
    # Prepare reply subject
    reply_subject = original_subject if original_subject.startswith("Re: ") else f"Re: {original_subject}"
    
    # Send the reply via SendGrid
    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email("hafnium49@gmail.com")  # Change to your verified sender
    to_email = To(sender_email)
    content = Content("text/plain", reply_body)
    
    mail = Mail(from_email, to_email, reply_subject, content)
    
    try:
        response = sg.client.mail.send.post(request_body=mail.get())
        print(f"✅ Reply sent to {sender_email} (Status: {response.status_code})")
        
        # Save the reply to database
        save_inbound_email(thread_id, sender_email, original_subject, inbound_body)
        save_outbound_reply(thread_id, sender_email, reply_subject, reply_body)
        
    except Exception as e:
        print(f"❌ Error sending reply: {str(e)}")


def extract_text_from_email(raw_email: str) -> str:
    """Extract plain text body from email"""
    # Simple extraction - in production, use email.parser
    lines = raw_email.split('\n')
    body_lines = []
    in_body = False
    
    for line in lines:
        if in_body:
            # Stop at reply separators
            if line.startswith('On ') and 'wrote:' in line:
                break
            if line.startswith('>'):
                continue
            body_lines.append(line)
        elif line.strip() == '':
            in_body = True
    
    return '\n'.join(body_lines).strip()


@app.route('/webhook/inbound', methods=['POST'])
def inbound_webhook():
    """Handle incoming emails from SendGrid Inbound Parse"""
    
    try:
        # Parse the incoming email data
        sender_email = request.form.get('from', '')
        subject = request.form.get('subject', '')
        text_body = request.form.get('text', '')
        html_body = request.form.get('html', '')
        
        # Extract sender name from email
        sender_name_match = re.match(r'^(.*?)\s*<(.+?)>$', sender_email)
        if sender_name_match:
            sender_name = sender_name_match.group(1).strip('"')
            sender_email = sender_name_match.group(2)
        else:
            sender_name = sender_email.split('@')[0]
        
        # Use text body, fallback to HTML
        email_body = text_body if text_body else html_body
        
        print(f"\n📧 Received email from: {sender_email}")
        print(f"📋 Subject: {subject}")
        print(f"💬 Body preview: {email_body[:100]}...")
        
        # Process reply asynchronously
        asyncio.run(generate_and_send_reply(sender_email, sender_name, email_body, subject))
        
        return jsonify({"status": "success", "message": "Email processed"}), 200
        
    except Exception as e:
        print(f"❌ Error processing webhook: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/webhook/test', methods=['GET', 'POST'])
def test_webhook():
    """Test endpoint to verify the webhook is working"""
    return jsonify({
        "status": "ok",
        "message": "Webhook server is running!",
        "timestamp": datetime.now().isoformat()
    })


@app.route('/conversations', methods=['GET'])
def list_conversations():
    """List all conversations (for debugging)"""
    conn = sqlite3.connect('email_conversations.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT thread_id, recipient_email, recipient_name, status, created_at, last_updated
        FROM conversations
        ORDER BY last_updated DESC
    ''')
    
    conversations = cursor.fetchall()
    conn.close()
    
    return jsonify({
        "conversations": [
            {
                "thread_id": conv[0],
                "recipient_email": conv[1],
                "recipient_name": conv[2],
                "status": conv[3],
                "created_at": conv[4],
                "last_updated": conv[5]
            }
            for conv in conversations
        ]
    })


if __name__ == '__main__':
    print("🚀 Starting SendGrid Webhook Server...")
    print("📡 Webhook endpoint: http://localhost:5000/webhook/inbound")
    print("🧪 Test endpoint: http://localhost:5000/webhook/test")
    print("📊 Conversations: http://localhost:5000/conversations")
    print("\n⚠️  Remember to expose this with ngrok: ngrok http 5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
