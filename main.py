import streamlit as st
from openai import OpenAI
from utils import extract_pdf_text

# Load PDF content
@st.cache_data
def load_benefits_summary():
    return extract_pdf_text("pdf_file_location")

client = OpenAI(api_key='apikey')

def get_completion(prompt, model="gpt-3.5-turbo"):
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful HR assistant for Valley Water. Answer only based on the Benefits Summary."},
            {"role": "user", "content": prompt},
        ]
    )
    return completion.choices[0].message.content

# Streamlit UI
st.title("📄 Valley Water HR Assistant (Benefits Focused)")
st.write("Ask a question about your employee benefits at Valley Water.")

question = st.text_input("Your HR question:")

if question:
    with st.spinner("Searching the Benefits Summary..."):
        pdf_text = load_benefits_summary()
        prompt = f"""Here is the Valley Water Benefits Summary:\n\n{pdf_text}\n\nNow answer this question:\n{question}"""
        response = get_completion(prompt)
        st.success("Answer:")
        st.write(response)
