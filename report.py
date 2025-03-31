import streamlit as st
from datetime import datetime
import pandas as pd
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key="api-key-here")

# Mock data - replace with actual chatbot data
MOCK_QA_LOG = [
    {"timestamp": "2024-01-01 09:00:00", "question": "How many vacation days do I get?", "answer": "Employees get 10 days in the first year, increasing with tenure."},
    {"timestamp": "2024-01-02 10:30:00", "question": "What's the retirement plan?", "answer": "We offer CalPERS with 2% at 62 formula for new members."},
    {"timestamp": "2024-01-03 11:15:00", "question": "Is dental insurance covered?", "answer": "Yes, Delta Dental is fully covered for all employees."},
    {"timestamp": "2024-01-04 14:00:00", "question": "How does sick leave work?", "answer": "12 days per year with unlimited accumulation."},
    {"timestamp": "2024-01-05 15:45:00", "question": "What medical plans are available?", "answer": "Blue Shield PPO, Blue Shield HMO and Kaiser HMO options."}
]

def summarize_conversations(qa_log):
    """Create token-efficient summary of conversations"""
    sample_questions = [qa['question'].split('?')[0][:30] for qa in qa_log[:5]]  # First 5 questions, 30 chars each
    return f"{len(qa_log)} conversations about: " + ", ".join(set(sample_questions))

def generate_faq_report(qa_log, instructions=""):
    """Generate concise FAQ analysis"""
    prompt = f"""Generate an HR FAQ summary based on employee queries. Structure the report as follows:
    Summary: Total number of questions and most common topics.
    Grouped FAQs: Categorize similar questions under relevant HR topics (e.g., Vacation, Benefits, Policies).
    Key Takeaways – Highlight patterns or recurring concerns.
    
    Instructions: {instructions or "None"}

    Format: Concise bullet points, max 15 items, with clear headings."""
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
    )
    return response.choices[0].message.content

def generate_sentiment_report(qa_log, instructions=""):
    """Generate sentiment analysis"""
    prompt = f""""Analyze sentiment trends:
    1. Sentiment Distribution (Percentage breakdown of positive, neutral, and negative interactions).
    2. Key Concerns: Identify recurring themes in negative or uncertain feedback.
    3. Recommendations: Suggested HR actions to address concerns and improve employee experience.

Instructions: {instructions or "None"}

Format: Bold headings, concise bullet points, max 400 tokens."""
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=400
    )
    return response.choices[0].message.content

def generate_actions_report(qa_log, instructions=""):
    """Generate action items"""
    prompt = f"""Extract HR action items:
    1. Urgent items (with deadlines) 
    2. Policy updates (needing clarification or revision)
    3. Training needs 

    Instructions: {instructions or 'None'}

    Format: Prioritized bullet list, max 10 items, with clear urgency levels"""
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=400
    )
    return response.choices[0].message.content

# Streamlit UI
st.set_page_config(page_title="Valley Water HR Insights", page_icon="💧")
st.title("💧 HR Analytics Dashboard")

# Initialize session state
if 'qa_log' not in st.session_state:
    st.session_state.qa_log = MOCK_QA_LOG.copy()

# Sidebar controls
with st.sidebar:
    report_type = st.selectbox(
        "Report Type",
        ["FAQ Report", "Sentiment Analysis", "Action Items"]
    )
    instructions = st.text_area(
        "Special Instructions",
        placeholder="E.g. 'most recent'",
        height=80
    )
    
    if st.button("Generate Report"):
        st.session_state.generate = True

# Main content
if st.session_state.get('generate'):
    with st.spinner(f"Creating {report_type}..."):
        try:
            if report_type == "FAQ Report":
                report = generate_faq_report(st.session_state.qa_log, instructions)
            elif report_type == "Sentiment Analysis":
                report = generate_sentiment_report(st.session_state.qa_log, instructions)
            else:
                report = generate_actions_report(st.session_state.qa_log, instructions)
            
            st.session_state.last_report = {
                "content": report,
                "type": report_type,
                "time": datetime.now().strftime("%m/%d %H:%M")
            }
            st.session_state.generate = False
        except Exception as e:
            st.error(f"Report generation failed: {str(e)}")

# Display report
if 'last_report' in st.session_state:
    st.subheader(f"{st.session_state.last_report['type']}")
    st.caption(f"Generated {st.session_state.last_report['time']}")
    st.markdown(st.session_state.last_report['content'])
    
    st.download_button(
        "📥 Download",
        data=st.session_state.last_report['content'],
        file_name=f"hr_report_{datetime.now().strftime('%Y%m%d')}.md"
    )

# Raw data (collapsed)
with st.expander("📊 View Conversation Samples", expanded=False):
    st.dataframe(pd.DataFrame(st.session_state.qa_log).head(5))