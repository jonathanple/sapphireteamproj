import streamlit as st
from openai import OpenAI
from sqlite_db import get_all_summaries

client = OpenAI(api_key='OPENAI_API_KEY')  # Replace with your key

def analyze_summaries(summaries, analysis_request):
    all_summaries_text = "\n".join([f"- {item[5]}" for item in summaries])
    prompt = f"""You are an HR data analyst. Analyze the following conversation summaries:\n\n{all_summaries_text}\n\nThe HR team has asked:\n{analysis_request}"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an expert HR analyst that evaluates employee concerns from chatbot conversations."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

# Streamlit UI for analysis
st.title("📊 Analyze Conversations (HR Only)")

analysis_prompt = st.text_area("Enter a request to analyze past conversations (e.g., 'What are the most common benefit concerns?')")

if st.button("Analyze"):
    summaries = get_all_summaries()
    if not summaries:
        st.warning("No conversation summaries found yet.")
    else:
        with st.spinner("Analyzing conversations..."):
            analysis_result = analyze_summaries(summaries, analysis_prompt)
            st.subheader("🧠 Analysis Result")
            st.write(analysis_result)
