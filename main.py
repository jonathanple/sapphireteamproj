import streamlit as st
from openai import OpenAI
from utils import extract_text_from_multiple_pdfs  # Update to use new method in utils
from sqlite_db import init_db, save_to_sqlite, get_all_summaries
import os

# Initialize OpenAI
client = OpenAI(api_key='OPENAI_API_KEY')  # Replace with your actual key

# Ensure SQLite DB exists
init_db()

# Function to get completion from OpenAI
def get_completion(prompt, model="gpt-3.5-turbo"):
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful HR assistant for Valley Water. Answer only based on the Benefits Summary and other relevant HR documents."},
            {"role": "user", "content": prompt},
        ]
    )
    return completion.choices[0].message.content.strip()

# Function to summarize the conversation for database storage only
def summarize_conversation(question, answer):
    prompt = f"""Summarize the following conversation between an employee and the HR assistant in a cohesive paragraph that includes the main points, the employee's question, and the assistant's answer:

    Employee: {question}
    Assistant: {answer}
    """
    summary = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that writes a concise summary of conversations, highlighting the question, answer, and main points."},
            {"role": "user", "content": prompt}
        ]
    )
    return summary.choices[0].message.content.strip()

# --- Streamlit UI ---

st.title("📄 Valley Water HR Assistant (Benefits and MOU Focused)")

# --- Chatbot Section ---
st.header("🤖 Ask the HR Assistant")
st.write("Ask a question about your employee benefits at Valley Water.")

question = st.text_input("Your HR question:")

# List of PDF files you want to extract text from (replace with your actual file paths)
pdf_file_paths = [
    "C:/Users/jonnyple/Desktop/ai4sg/Benefits_Summary.pdf",
    "C:/Users/jonnyple/Desktop/ai4sg/EA_Article 15 Section 3_Grievance Procedure (3).pdf",
    "C:/Users/jonnyple/Desktop/ai4sg/Employees Association MOU 2022-2025.docx (3).pdf",
    "C:/Users/jonnyple/Desktop/ai4sg/Employer-Employee Relations Rules - Approved 8-23-2011- Resolution 11-60.pdf",
    "C:/Users/jonnyple/Desktop/ai4sg/Engineers Society MOU 2022-2025.docx (1).pdf",
    "C:/Users/jonnyple/Desktop/ai4sg/ES_PMA_Article 14 Section 3_Grievance Procedure.pdf",
    "C:/Users/jonnyple/Desktop/ai4sg/Final MEA Document Signed.pdf",
    "C:/Users/jonnyple/Desktop/ai4sg/Professional Land Surveyor License Differential Side Letter.pdf",
    "C:/Users/jonnyple/Desktop/ai4sg/Professional Managers Association MOU 2022-2025.docx (1).pdf",
    "C:/Users/jonnyple/Desktop/ai4sg/Water Distribution Certification Differential Side Letter.docx.pdf"
]

if st.button("Submit Question") and question:
    with st.spinner("Searching the HR documents..."):
        # Extract text from all the HR PDFs (Benefits + Bargaining MOUs)
        hr_documents = extract_text_from_multiple_pdfs(pdf_file_paths)

        # Combine all the extracted text into a single prompt
        all_text = "\n\n".join(hr_documents.values())
        prompt = f"""Here is the HR information:\n\n{all_text}\n\nNow answer this question:\n{question}"""
        response = get_completion(prompt)

        # Summarize the conversation for saving to the database (but not displaying to the user)
        summary = summarize_conversation(question, response)

        # Save the conversation summary to SQLite
        save_to_sqlite(None, None, question, response, summary)

        # Display the result to the user (without the summary)
        st.success("Answer:")
        st.write(response)
