import streamlit as st
from openai import OpenAI
from utils import extract_pdf_text
import json
import os

# Load PDF content
@st.cache_data
def load_benefits_summary():
    return extract_pdf_text("C:/Users/jonat/Downloads/Benefits_Summary.pdf")

# Initialize OpenAI
client = OpenAI(api_key='OPENAI_API_KEY')  # Replace with your actual key

def get_completion(prompt, model="gpt-3.5-turbo"):
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful HR assistant for Valley Water. Answer only based on the Benefits Summary."},
            {"role": "user", "content": prompt},
        ]
    )
    return completion.choices[0].message.content.strip()

def summarize_conversation(question, answer):
    prompt = f"""Summarize the following conversation between an employee and the HR assistant in 2-3 sentences:\n
    Employee: {question}\n
    Assistant: {answer}
    """
    summary = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that writes short summaries of conversations."},
            {"role": "user", "content": prompt}
        ]
    )
    return summary.choices[0].message.content.strip()

# Save to JSON file
SUMMARY_DB_PATH = "chat_summaries.json"

def save_summary_to_db(summary, question, answer):
    record = {
        "summary": summary,
        "question": question,
        "answer": answer
    }

    if os.path.exists(SUMMARY_DB_PATH):
        with open(SUMMARY_DB_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = []

    data.append(record)

    with open(SUMMARY_DB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def load_summaries():
    if not os.path.exists(SUMMARY_DB_PATH):
        return []
    with open(SUMMARY_DB_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def analyze_summaries(summaries, analysis_request):
    all_summaries_text = "\n".join([f"- {item['summary']}" for item in summaries])
    prompt = f"""You are an HR data analyst. Analyze the following conversation summaries:\n\n{all_summaries_text}\n\nThe HR team has asked:\n{analysis_request}"""
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an expert HR analyst that evaluates employee concerns from chatbot conversations."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

# --- Streamlit UI ---

st.title("📄 Valley Water HR Assistant (Benefits Focused)")

# --- Chatbot Section ---
st.header("🤖 Ask the HR Assistant")
st.write("Ask a question about your employee benefits at Valley Water.")
question = st.text_input("Your HR question:")

if question:
    with st.spinner("Searching the Benefits Summary..."):
        pdf_text = load_benefits_summary()
        prompt = f"""Here is the Valley Water Benefits Summary:\n\n{pdf_text}\n\nNow answer this question:\n{question}"""
        response = get_completion(prompt)

        # Summarize & save
        summary = summarize_conversation(question, response)
        save_summary_to_db(summary, question, response)

        # Display
        st.success("Answer:")
        st.write(response)

        st.info("📌 Conversation Summary:")
        st.write(summary)

# --- Analysis Section ---
st.header("📊 Analyze Conversations (HR Only)")
analysis_prompt = st.text_area("Enter a request to analyze past conversations (e.g., 'What are the most common benefit concerns?')")

if st.button("Analyze"):
    summaries = load_summaries()
    if not summaries:
        st.warning("No conversation summaries found yet.")
    else:
        with st.spinner("Analyzing conversations..."):
            analysis_result = analyze_summaries(summaries, analysis_prompt)
            st.subheader("🧠 Analysis Result")
            st.write(analysis_result)
