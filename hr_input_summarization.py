import streamlit as st
from openai import OpenAI
from PyPDF2 import PdfReader
import pytesseract
from PIL import Image
import os
import sqlite3
from datetime import datetime

# ===================== DATABASE SETUP =====================
DB_PATH = os.path.join(os.path.dirname(__file__), "v2_hr_input_summaries.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS v2_hr_input_summaries (
            store_id INTEGER PRIMARY KEY AUTOINCREMENT,
            summary TEXT,
            employee_id TEXT,
            input_date TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_to_sqlite(summary, employee_ID, input_date=None):
    if input_date is None:
        input_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO v2_hr_input_summaries (summary, employee_id, input_date)
        VALUES (?, ?, ?)
    ''', (summary, employee_ID, input_date))
    conn.commit()
    conn.close()

init_db()

# ===================== OPENAI SETUP =====================
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# ===================== EXTRACT FUNCTIONS =====================
def extract_text_from_image(image_file):
    img = Image.open(image_file)
    return pytesseract.image_to_string(img)

def transcribe_audio(audio_file_path):
    with open(audio_file_path, "rb") as f:
        transcription = client.audio.transcriptions.create(model="whisper-1", file=f)
    return transcription.text

def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text
    return text

def abstract_summary_extraction(transcription):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": "You are a highly skilled AI trained in language comprehension and summarization. I would like you to read the following text and summarize the key points"
            },
            {
                "role": "user",
                "content": transcription
            }
        ]
    )
    return response.choices[0].message.content

# ===================== STREAMLIT UI =====================
input_option = st.selectbox('Choose an input type:', ['Text Input', 'Screenshot Input', 'PDF Input', 'Recording Input'])

# ---------- TEXT INPUT ----------
if input_option == 'Text Input':
    st.subheader('Enter your text:')
    text_input = st.text_area("Input your text here")

    if text_input:
        if "text_summary" not in st.session_state:
            with st.spinner("Summarizing with AI..."):
                st.session_state.text_summary = abstract_summary_extraction(text_input)

        st.subheader("Summary of Key Points:")
        st.write(st.session_state.text_summary)

        employee_id = st.text_input("Enter your employee ID to save this summary:")
        if employee_id and st.button("Save Summary"):
            save_to_sqlite(st.session_state.text_summary, employee_id)
            st.success("Summary saved to database.")
            del st.session_state.text_summary

# ---------- SCREENSHOT INPUT ----------
elif input_option == 'Screenshot Input':
    st.subheader('Upload a screenshot:')
    screenshot_input = st.file_uploader("Upload screenshot", type=['png', 'jpg', 'jpeg'])

    if screenshot_input is not None:
        st.image(screenshot_input, caption='Uploaded screenshot', use_column_width=True)

        with st.spinner("Extracting text from image..."):
            extracted_text = extract_text_from_image(screenshot_input)
            st.subheader("Extracted Text:")
            st.write(extracted_text)

        if extracted_text.strip():
            if "screenshot_summary" not in st.session_state:
                with st.spinner("Summarizing with AI..."):
                    st.session_state.screenshot_summary = abstract_summary_extraction(extracted_text)

            st.subheader("Summary of Key Points:")
            st.write(st.session_state.screenshot_summary)

            employee_id = st.text_input("Enter your employee ID to save this summary:", key="screenshot_id")
            if employee_id and st.button("Save Summary", key="save_screenshot"):
                save_to_sqlite(st.session_state.screenshot_summary, employee_id)
                st.success("Summary saved to database.")
                del st.session_state.screenshot_summary
        else:
            st.warning("No readable text found in the image.")

# ---------- PDF INPUT ----------
elif input_option == 'PDF Input':
    st.subheader('Upload a PDF:')
    pdf_input = st.file_uploader("Upload PDF", type=['pdf'])

    if pdf_input is not None:
        st.write("PDF file uploaded successfully!")
        st.write(f"Filename: {pdf_input.name}")

        with st.spinner("Extracting text from PDF..."):
            extracted_text = extract_text_from_pdf(pdf_input)
            cleaned_text = ' '.join(extracted_text.splitlines())
            st.subheader("Extracted Text:")
            st.write(cleaned_text)

        if cleaned_text.strip():
            if "pdf_summary" not in st.session_state:
                with st.spinner("Summarizing with AI..."):
                    st.session_state.pdf_summary = abstract_summary_extraction(cleaned_text)

            st.subheader("Summary of Key Points:")
            st.write(st.session_state.pdf_summary)

            employee_id = st.text_input("Enter your employee ID to save this summary:", key="pdf_id")
            if employee_id and st.button("Save Summary", key="save_pdf"):
                save_to_sqlite(st.session_state.pdf_summary, employee_id)
                st.success("Summary saved to database.")
                del st.session_state.pdf_summary
        else:
            st.warning("No readable text found in the PDF.")

# ---------- RECORDING INPUT ----------
elif input_option == 'Recording Input':
    st.subheader('Upload a Call:')
    recording_input = st.file_uploader("Upload MP3 file", type=['mp3'])

    if recording_input is not None:
        st.audio(recording_input, format='audio/mp3')

        with open("temp.mp3", "wb") as f:
            f.write(recording_input.read())

        with st.spinner("Transcribing audio..."):
            transcribed_text = transcribe_audio("temp.mp3")
            cleaned_text = ' '.join(transcribed_text.splitlines())
            st.subheader("Transcribed Text:")
            st.write(cleaned_text)

        if cleaned_text.strip():
            if "audio_summary" not in st.session_state:
                with st.spinner("Summarizing with AI..."):
                    st.session_state.audio_summary = abstract_summary_extraction(cleaned_text)

            st.subheader("Summary of Key Points:")
            st.write(st.session_state.audio_summary)

            employee_id = st.text_input("Enter your employee ID to save this summary:", key="audio_id")
            if employee_id and st.button("Save Summary", key="save_audio"):
                save_to_sqlite(st.session_state.audio_summary, employee_id)
                st.success("Summary saved to database.")
                del st.session_state.audio_summary
        else:
            st.warning("No transcribed text found.")
