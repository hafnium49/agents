"""
Helper script to populate the Q&A knowledge base with sample questions and answers.
Run this script to add initial Q&A pairs to the database.
"""

import sqlite3


def populate_sample_qa():
    """Populate the database with sample Q&A pairs"""
    conn = sqlite3.connect('career_assistant.db')
    cursor = conn.cursor()

    sample_qa = [
        # Skills category
        ("What programming languages do you know?",
         "I'm proficient in Python, JavaScript, TypeScript, and have experience with SQL, Java, and Go.",
         "skills"),

        ("What AI/ML frameworks are you familiar with?",
         "I work extensively with PyTorch, TensorFlow, LangChain, LangGraph, CrewAI, AutoGen, and the OpenAI/Anthropic APIs.",
         "skills"),

        ("Do you have experience with cloud platforms?",
         "Yes, I have experience deploying applications on AWS, Google Cloud Platform, and Hugging Face Spaces.",
         "skills"),

        # Experience category
        ("What's your experience with AI agents?",
         "I teach a comprehensive course on Agentic AI Engineering, covering multiple frameworks and real-world applications. I've built production AI systems using various agent architectures.",
         "experience"),

        ("Have you worked on any notable projects?",
         "Yes, I've built AI agent systems for research, debate simulations, browser automation, and career assistants. I also maintain an open-source educational repository on agentic AI.",
         "experience"),

        # Education category
        ("What's your educational background?",
         "I have a strong technical background with extensive experience in software engineering and AI/ML. I'm also an educator, teaching thousands of students about AI agent development.",
         "education"),

        # Availability
        ("Are you available for consulting or freelance work?",
         "I'm selective about projects but open to interesting opportunities. Please share details about your project and your contact information so we can discuss further.",
         "availability"),

        ("What's your hourly rate?",
         "My rates vary depending on the project scope and complexity. I'd be happy to discuss this after learning more about your specific needs. Please provide your email so we can continue the conversation.",
         "availability"),

        # Teaching
        ("Do you offer training or workshops?",
         "Yes! I offer comprehensive training on AI agent development, covering multiple frameworks and practical applications. I can customize workshops for teams. Let's discuss your training needs - please share your contact details.",
         "teaching"),
    ]

    # Insert sample Q&A
    for question, answer, category in sample_qa:
        cursor.execute(
            'INSERT INTO qa_knowledge (question, answer, category) VALUES (?, ?, ?)',
            (question, answer, category)
        )

    conn.commit()
    count = cursor.execute('SELECT COUNT(*) FROM qa_knowledge').fetchone()[0]
    conn.close()

    print(f"✓ Successfully added {len(sample_qa)} Q&A pairs to the database")
    print(f"✓ Total Q&A pairs in database: {count}")


if __name__ == "__main__":
    populate_sample_qa()
