# 🚀 Automated Email Reply System - Setup Guide

This is a complete implementation of the HARD CHALLENGE from the lab: automated email reply handling using SendGrid webhooks and AI agents.

## 📋 Overview

The system automatically:
1. Tracks all outbound cold emails
2. Receives replies via SendGrid webhook
3. Analyzes conversation context with AI
4. Generates and sends contextual responses
5. Maintains conversation history in a database

## 🏗️ Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   SendGrid  │─────>│   Webhook    │─────>│     AI      │
│  (Inbound)  │      │    Server    │      │    Agent    │
└─────────────┘      └──────────────┘      └─────────────┘
                            │                      │
                            ↓                      ↓
                     ┌──────────────┐      ┌─────────────┐
                     │   Database   │      │  SendGrid   │
                     │  (Tracking)  │      │  (Outbound) │
                     └──────────────┘      └─────────────┘
```

## 📦 Installation

### 1. Install Dependencies

```bash
cd 2_openai
uv pip install flask python-dotenv sendgrid openai-agents ngrok
```

### 2. Set Up Environment Variables

Add to your `.env` file:

```bash
SENDGRID_API_KEY=your_sendgrid_api_key
OPENAI_API_KEY=your_openai_api_key
```

### 3. Initialize Database

The database is automatically created when you run the notebook cells. It creates:
- `conversations` table: Tracks email threads
- `messages` table: Stores all email messages

## 🚀 Running the Webhook Server

### Development (Local)

1. **Start the webhook server:**
```bash
cd 2_openai
uv run python webhook_server.py
```

The server will start on `http://localhost:5000`

2. **Expose with ngrok (in another terminal):**
```bash
ngrok http 5000
```

Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)

### Production Deployment

Deploy to any of these platforms:

#### Option A: Railway.app (Easiest)
1. Push code to GitHub
2. Connect Railway to your repo
3. Add environment variables
4. Railway will auto-deploy

#### Option B: Heroku
```bash
heroku create your-app-name
heroku config:set SENDGRID_API_KEY=xxx OPENAI_API_KEY=xxx
git push heroku main
```

#### Option C: AWS Lambda + API Gateway
- Use Zappa or AWS SAM
- Configure API Gateway trigger
- Set environment variables

## ⚙️ SendGrid Configuration

### 1. Configure Inbound Parse

1. Go to **SendGrid Dashboard**: https://app.sendgrid.com/
2. Navigate: **Settings** → **Inbound Parse** → **Add Host & URL**
3. Fill in:
   - **Domain**: Your domain (e.g., `yourdomain.com`)
   - **Subdomain**: `reply` (or any subdomain)
   - **Destination URL**: `https://your-ngrok-or-production-url.com/webhook/inbound`
   - ✅ Check: "POST the raw, full MIME message"
4. Click **Add**

### 2. Update DNS Records

Add an MX record in your domain's DNS:

```
Type:     MX
Host:     reply
Value:    mx.sendgrid.net
Priority: 10
TTL:      3600
```

### 3. Verify Setup

Test your webhook:
```bash
curl https://your-url.com/webhook/test
```

Should return: `{"status": "ok", "message": "Webhook server is running!"}`

## 📧 Sending Tracked Emails

Use the `send_tracked_email` function in your notebook:

```python
result = send_tracked_email(
    recipient_email="alice@example.com",
    recipient_name="Alice Johnson", 
    subject="Your Subject Here",
    body="Your email body here"
)
```

The email is automatically tracked with a unique thread ID.

## 🔄 How Replies Work

1. **Recipient replies** to your email
2. **SendGrid** receives the reply (via MX record)
3. **Inbound Parse** webhook forwards to your server
4. **Webhook handler** extracts email data
5. **Database** loads conversation history
6. **AI Agent** analyzes context and generates response
7. **SendGrid API** sends automated reply
8. **Database** saves both messages

All happens automatically in seconds! ⚡

## 📊 Monitoring Conversations

### View All Conversations

Run in the notebook:
```python
view_all_conversations()
```

### Via API

```bash
curl http://localhost:5000/conversations
```

### Database Query

```sql
SELECT * FROM conversations ORDER BY last_updated DESC;
SELECT * FROM messages WHERE thread_id = 'your-thread-id';
```

## 🧪 Testing

### 1. Simulate a Conversation

Run the simulation cell in the notebook:
```python
simulate_full_conversation_flow()
```

### 2. Test Webhook Locally

```bash
curl -X POST http://localhost:5000/webhook/inbound \
  -F "from=Alice Johnson <alice@example.com>" \
  -F "subject=Re: Your Email" \
  -F "text=This is a test reply"
```

### 3. End-to-End Test

1. Send a real email using `send_tracked_email`
2. Reply to that email from your inbox
3. Watch the webhook logs for processing
4. Check your inbox for the automated response

## 🔒 Security Considerations

### Production Checklist:

- [ ] Add webhook authentication (shared secret)
- [ ] Implement rate limiting
- [ ] Validate sender domains
- [ ] Sanitize email inputs
- [ ] Use HTTPS only
- [ ] Add logging and monitoring
- [ ] Set up error alerting
- [ ] Implement retry logic
- [ ] Add unsubscribe handling
- [ ] GDPR compliance measures

### Example: Webhook Authentication

```python
@app.route('/webhook/inbound', methods=['POST'])
def inbound_webhook():
    # Verify webhook signature
    signature = request.headers.get('X-Webhook-Signature')
    if not verify_signature(signature, request.data):
        return jsonify({"error": "Unauthorized"}), 401
    # ... rest of handler
```

## 🐛 Troubleshooting

### Issue: No email received at webhook

**Check:**
1. MX record is properly configured (use `dig reply.yourdomain.com MX`)
2. SendGrid Inbound Parse is enabled
3. Webhook URL is correct and accessible
4. Check SendGrid activity logs

### Issue: Webhook returns 500 error

**Check:**
1. Server logs: `tail -f webhook_server.log`
2. Database file exists and is writable
3. Environment variables are set
4. OpenAI API key is valid

### Issue: Replies not being sent

**Check:**
1. SendGrid API key has "Mail Send" permission
2. Sender email is verified in SendGrid
3. Check SendGrid activity for bounces
4. Review database for conversation records

### Issue: ngrok tunnel closed

**Solution:**
- Free ngrok tunnels expire after 2 hours
- Use `ngrok http 5000 --region us` to reconnect
- Update SendGrid with new URL
- Consider upgrading ngrok or deploying to production

## 📈 Scaling Considerations

### For High Volume (>1000 emails/day)

1. **Use async task queue** (Celery + Redis)
```python
@celery.task
def process_inbound_email(email_data):
    # Process asynchronously
```

2. **Database optimization**
- Use PostgreSQL instead of SQLite
- Add indexes on thread_id and recipient_email
- Archive old conversations

3. **Caching**
- Cache conversation histories (Redis)
- Cache AI responses for similar queries

4. **Load balancing**
- Deploy multiple webhook servers
- Use nginx or AWS ALB

5. **Monitoring**
- Set up Prometheus + Grafana
- Track response times, error rates
- Alert on failures

## 🎯 Advanced Features to Add

1. **Sentiment Analysis**: Detect urgent/negative replies
2. **Smart Routing**: Escalate to human for complex queries
3. **A/B Testing**: Test different AI prompts
4. **Lead Scoring**: Track engagement levels
5. **CRM Integration**: Sync with Salesforce/HubSpot
6. **Analytics Dashboard**: Visualize conversation metrics
7. **Multi-language**: Detect and respond in recipient's language
8. **Scheduling**: Suggest meeting times automatically

## 📚 Additional Resources

- [SendGrid Inbound Parse Docs](https://docs.sendgrid.com/for-developers/parsing-email/inbound-email)
- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [ngrok Documentation](https://ngrok.com/docs)

## 💡 Tips & Best Practices

1. **Always test in sandbox mode first**
2. **Monitor AI responses** - review before going fully automated
3. **Set daily send limits** to avoid spam issues
4. **Implement graceful degradation** if AI fails
5. **Keep conversation context brief** (last 5 messages max)
6. **Add human review for high-value leads**
7. **Track metrics**: response time, conversion rate, etc.

## 🤝 Contributing

Found a bug or have an enhancement? This is part of the course lab, but feel free to:
- Add more sophisticated reply logic
- Improve the AI prompts
- Add better error handling
- Create a web dashboard

---

**Built as part of the Autonomous AI Agents course** 🎓

Happy automating! 🚀
