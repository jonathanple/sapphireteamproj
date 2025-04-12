import streamlit as st
from openai import OpenAI
from utils import extract_pdf_text
import json
import os

# Load PDF content
@st.cache_data
def load_benefits_summary():
    return extract_pdf_text("Benefits_Summary.pdf")  # Replace with your actual PDF path

# Initialize OpenAI client
client = OpenAI(api_key='OPENAI_API_KEY')  # Replace with your actual key or use env var

# Get completion from GPT
def get_completion(prompt, model="gpt-3.5-turbo"):
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful HR assistant for Valley Water. Answer only based on the Benefits Summary."},
            {"role": "user", "content": prompt},
        ]
    )
    return completion.choices[0].message.content.strip()

# Summarize the conversation
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

# Save summary to local JSON "database"
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

# Streamlit UI
st.title("📄 Valley Water HR Assistant (Benefits Focused)")
st.write("Ask a question about your employee benefits at Valley Water.")

question = st.text_input("Your HR question:")

if question:
    with st.spinner("Searching the Benefits Summary..."):
        pdf_text = load_benefits_summary()
        prompt = f"""Here is the Valley Water Benefits Summary:\n\n{pdf_text}\n\nNow answer this question:\n{question}"""
        response = get_completion(prompt)

        # Summarize and save conversation
        summary = summarize_conversation(question, response)
        save_summary_to_db(summary, question, response)

        # Display results
        st.success("Answer:")
        st.write(response)

        st.info("📌 Conversation Summary:")
        st.write(summary)
