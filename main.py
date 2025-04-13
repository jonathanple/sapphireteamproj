import streamlit as st
from openai import OpenAI
from utils import extract_pdf_text
from sqlite_db import init_db, save_to_sqlite, get_all_summaries
import os

# Load PDF content
@st.cache_data
def load_benefits_summary():
    return extract_pdf_text("C:/Users/jonat/OneDrive/Desktop/ai4sg project/Benefits_Summary.pdf")

# Initialize OpenAI
client = OpenAI(api_key='OPENAI_API_KEY')  # Replace with your actual key

# Ensure SQLite DB exists
init_db()

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

# --- Streamlit UI ---

st.title("📄 Valley Water HR Assistant (Benefits Focused)")

# --- Chatbot Section ---
st.header("🤖 Ask the HR Assistant")
st.write("Ask a question about your employee benefits at Valley Water.")

employee_id = st.text_input("Employee ID")
employee_name = st.text_input("Employee Name")
question = st.text_input("Your HR question:")

if st.button("Submit Question") and question and employee_id and employee_name:
    with st.spinner("Searching the Benefits Summary..."):
        pdf_text = load_benefits_summary()
        prompt = f"""Here is the Valley Water Benefits Summary:\n\n{pdf_text}\n\nNow answer this question:\n{question}"""
        response = get_completion(prompt)

        # Summarize & save to SQLite
        summary = summarize_conversation(question, response)
        save_to_sqlite(employee_id, employee_name, question, response, summary)

        # Display
        st.success("Answer:")
        st.write(response)

        


