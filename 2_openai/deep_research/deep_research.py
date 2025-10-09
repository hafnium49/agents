import gradio as gr
from dotenv import load_dotenv
from research_manager_v2 import ResearchManagerV2

load_dotenv(override=True)

# Global state to store questions and query
state = {
    "query": None,
    "questions": None
}


async def generate_questions(query: str):
    """Step 1: Generate clarification questions"""
    if not query.strip():
        return "Please enter a research query.", "", "", "", gr.update(visible=False)
    
    state["query"] = query
    manager = ResearchManagerV2()
    
    try:
        questions = await manager.generate_clarification_questions(query)
        state["questions"] = questions
        
        # Return questions and show clarification section
        return (
            f"**Great! To help refine your research, please answer these questions:**\n\n*{questions.reasoning}*",
            questions.question1,
            questions.question2,
            questions.question3,
            gr.update(visible=True)
        )
    except Exception as e:
        return f"Error generating questions: {str(e)}", "", "", "", gr.update(visible=False)


async def run_research(answer1: str, answer2: str, answer3: str):
    """Step 2: Run research with clarifications"""
    if not state["query"] or not state["questions"]:
        yield "Error: Please start with a query first."
        return
    
    # Build clarifications dictionary
    clarifications = {
        state["questions"].question1: answer1 or "No specific preference",
        state["questions"].question2: answer2 or "No specific preference",
        state["questions"].question3: answer3 or "No specific preference"
    }
    
    manager = ResearchManagerV2()
    async for chunk in manager.run(state["query"], clarifications):
        yield chunk


with gr.Blocks(theme=gr.themes.Default(primary_hue="sky")) as ui:
    gr.Markdown("# Deep Research")
    gr.Markdown("Get comprehensive research reports with clarification-driven searches")
    
    # Step 1: Query Input
    with gr.Group():
        gr.Markdown("### Step 1: Enter Your Research Query")
        query_textbox = gr.Textbox(
            label="What topic would you like to research?",
            placeholder="e.g., AI agent frameworks, Climate change impact on agriculture",
            lines=2
        )
        ask_button = gr.Button("Generate Clarification Questions", variant="primary")
    
    # Step 2: Clarification Questions (initially hidden)
    with gr.Group(visible=False) as clarification_section:
        gr.Markdown("### Step 2: Answer Clarification Questions")
        reasoning_text = gr.Markdown()
        
        question1_label = gr.Markdown()
        answer1 = gr.Textbox(label="Answer 1", placeholder="Your answer...", lines=2)
        
        question2_label = gr.Markdown()
        answer2 = gr.Textbox(label="Answer 2", placeholder="Your answer...", lines=2)
        
        question3_label = gr.Markdown()
        answer3 = gr.Textbox(label="Answer 3", placeholder="Your answer...", lines=2)
        
        research_button = gr.Button("Start Research", variant="primary")
    
    # Step 3: Results
    with gr.Group():
        gr.Markdown("### Research Report")
        report = gr.Markdown(label="Report")
    
    # Event handlers
    ask_button.click(
        fn=generate_questions,
        inputs=[query_textbox],
        outputs=[reasoning_text, question1_label, question2_label, question3_label, clarification_section]
    )
    
    research_button.click(
        fn=run_research,
        inputs=[answer1, answer2, answer3],
        outputs=report
    )

ui.launch(inbrowser=True)

