# Enhanced Career Conversation Assistant

This is an enhanced version of the career conversation app from Lab 4, implementing the exercise suggestions with additional agentic patterns and features.

## What's New

### 1. **SQLite Database Integration**
- **Q&A Knowledge Base**: Store and retrieve frequently asked questions
- **Conversation Logging**: Track all conversations for analytics
- **Leads Database**: Persist user contact information

### 2. **Additional Tools**
- `search_qa_database`: Search the knowledge base before saying "I don't know"
- `add_qa_to_database`: Add new Q&A pairs to the knowledge base
- Enhanced `record_user_details`: Now saves to database in addition to push notifications

### 3. **Agentic Patterns from Lab 2**
- **Reflection Pattern**: Automatically reflects on and improves longer answers
- **Tool Chaining**: Searches knowledge base before falling back to "don't know"
- **Structured Logging**: Tracks conversation patterns for future improvements

### 4. **Enhanced UI**
- Custom theme with better visual design
- Example prompts to guide users
- Better title and description
- Custom CSS styling

## Files

- `app_enhanced.py`: Enhanced application with all new features
- `populate_qa_db.py`: Helper script to populate sample Q&A data
- `career_assistant.db`: SQLite database (created on first run)

## Setup & Usage

### 1. Install Dependencies
Already included in the project's `pyproject.toml`:
```bash
uv sync
```

### 2. Populate the Knowledge Base (Optional)
```bash
uv run python populate_qa_db.py
```

### 3. Run the Enhanced App
```bash
uv run python app_enhanced.py
```

The app will launch at http://localhost:7860

## Key Enhancements Explained

### Knowledge Base Search Flow
1. User asks a question
2. App first searches the Q&A database using `search_qa_database` tool
3. If found, uses that information in the response
4. If not found, uses context from LinkedIn/summary
5. If still can't answer, records the unknown question

### Reflection Pattern
- For substantial responses (>50 characters), the app uses a second LLM call
- Reviews the initial answer for clarity, completeness, and professionalism
- Returns an improved version if needed

### Database Schema

**qa_knowledge table:**
- `id`: Primary key
- `question`: The question text
- `answer`: The answer text
- `category`: Classification (skills, experience, education, etc.)
- `created_at`: Timestamp

**conversation_logs table:**
- `id`: Primary key
- `user_message`: User's message
- `assistant_response`: Assistant's response
- `timestamp`: Conversation time

**leads table:**
- `id`: Primary key
- `name`: User's name
- `email`: User's email (required)
- `notes`: Additional context
- `timestamp`: When recorded

## Deployment to Hugging Face

The enhanced version can be deployed the same way as the original:

```bash
cd 1_foundations
uv run gradio deploy
```

Follow the prompts and specify:
- App file: `app_enhanced.py`
- Hardware: `cpu-basic`
- Secrets: Your API keys and Pushover credentials

**Note**: The SQLite database will be created on the Hugging Face Space, but will be ephemeral (resets on restart). For production, consider using a persistent database solution.

## Customization

### Add Your Own Q&A Pairs
Edit `populate_qa_db.py` to add your specific Q&A pairs, or manually add them through the tool interface.

### Adjust Reflection Behavior
In `app_enhanced.py`, modify:
```python
self.use_reflection = True  # Set to False to disable
```

### Categories
Customize Q&A categories based on your needs:
- skills
- experience
- education
- projects
- availability
- teaching
- consulting
- etc.

## Future Enhancements

Potential additions you could implement:

1. **Vector Search**: Replace keyword search with embedding-based semantic search
2. **Multi-Model Evaluation**: Use pattern from Lab 2 to evaluate responses with multiple models
3. **RAG Implementation**: Add document chunking and vector database for better context retrieval
4. **Analytics Dashboard**: Visualize conversation patterns and common questions
5. **Email Integration**: Automatically send follow-up emails to leads
6. **Calendar Integration**: Allow users to book meetings directly
7. **File Upload**: Let users upload their resume for comparison
8. **Export Functionality**: Export conversation logs and leads to CSV

## Commercial Applications

This enhanced pattern is applicable to:
- **Customer Support**: Knowledge base + conversation logging
- **Lead Generation**: Capture and qualify leads automatically
- **Sales Assistants**: Product Q&A with contact capture
- **HR Screening**: Pre-interview questionnaires with database storage
- **Expert Systems**: Domain-specific Q&A with continuous learning

## License

Same as the original course materials - for educational purposes.
