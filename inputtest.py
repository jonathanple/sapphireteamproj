import streamlit as st
from openai import OpenAI
from PyPDF2 import PdfReader
import pytesseract
from PIL import Image
import os


api_key = os.getenv("OPENAI_API_KEY")
print("API Key:", api_key)  # Check if the API key is being loaded correctly

# Initialize the OpenAI client
client = OpenAI(api_key=api_key)


# Image to text
def extract_text_from_image(image_file):
    img = Image.open(image_file)
    text = pytesseract.image_to_string(img)
    return text

# Audio to text
def transcribe_audio(audio_file_path):
  audio_file = open(audio_file_path, "rb")
  transcription = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
  return transcription.text

#PDF to text
def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text


# HR input special instructions









# Summarize user input
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

# Streamlit UI
input_option = st.selectbox('Choose an input type:', ['Text Input', 'Screenshot Input', 'PDF Input', 'Recording Input'])


if input_option == 'Text Input':
    st.subheader('Enter your text:')
    text_input = st.text_area("Input your text here")
    summary = abstract_summary_extraction(text_input)
    st.write(summary)


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
            with st.spinner("Summarizing with AI..."):
                summary = abstract_summary_extraction(extracted_text)
                st.subheader("Summary of Key Points:")
                st.write(summary)
        else:
            st.warning("No readable text found in the image.")


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
            with st.spinner("Summarizing with AI..."):
                summary = abstract_summary_extraction(cleaned_text)
                st.subheader("Summary of Key Points:")
                st.write(summary)
        else:
            st.warning("No readable text found in the PDF.")


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
            with st.spinner("Summarizing with AI..."):
                summary = abstract_summary_extraction(cleaned_text)
                st.subheader("Summary of Key Points:")
                st.write(summary)
        else:
            st.warning("No transcribed text found.")
                 



