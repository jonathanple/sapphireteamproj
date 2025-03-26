import streamlit as st
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key="my-api-key-here")


# Function to generate AI advice
def get_completion(prompt, model="gpt-3.5-turbo"):
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a HR Chatbot for Valley Water and you provide answers for employee questions."},
            {"role": "user", "content": prompt},
        ]
    )
    return completion.choices[0].message.content

# Function to generate an AI image
def get_image(prompt, model="dall-e-2"):
    # Generate 1 image related to the given prompt
    image = client.images.generate(
        prompt=prompt,
        model=model,
        n=1,  # Generate only 1 image
        size="1024x1024"
    )
    # Return the URL of the generated image
    return image.data[0].url

# Create the Streamlit app
st.title("Career Advisor")

#Streamlit color
st.markdown(
    """
    <style>
         .stApp {
            background-color: #FFB5C0!important;
        }
        input, textarea {
            background-color: #FFD1DC!important;
        }
    </style>
    <
    """,
    unsafe_allow_html=True
)

# Initialize session state
if "step" not in st.session_state:
    st.session_state.step = 1  # Tracks the current step/question
if "responses" not in st.session_state:
    st.session_state.responses = {}  # Stores user's responses

# Function to handle responses and progress
def handle_response(question_key, user_input):
    if user_input:  # Save the response only if it's not empty
        st.session_state.responses[question_key] = user_input
        st.session_state.step += 1  # Proceed to the next question

# Start conversation
st.write("Hi there! I’m here to help you explore your career options. Please answer a few questions to get started.")

# Render all questions statically
st.write("### Questions:")

# Question 1: Major
if "major" in st.session_state.responses:
    st.write(f"**1. What's your major?**\n{st.session_state.responses['major']}")
else:
    with st.form(key="form_major"):
        major = st.text_input("What's your major? (Step 1)")
        submitted = st.form_submit_button("Submit")
        if submitted and major:
            handle_response("major", major)
            st.rerun()  # Force the app to rerun and update the UI

# Question 2: Favorite Subject
if "favorite_subject" in st.session_state.responses:
    st.write(f"**2. What's your favorite subject?**\n{st.session_state.responses['favorite_subject']}")
else:
    if st.session_state.step >= 2:
        with st.form(key="form_subject"):
            fav_subject = st.text_input("What's your favorite subject? (Step 2)")
            submitted = st.form_submit_button("Submit")
            if submitted and fav_subject:
                handle_response("favorite_subject", fav_subject)
                st.rerun()  # Force the app to rerun and update the UI

# Question 3: Desired Field
if "field_interest" in st.session_state.responses:
    st.write(f"**3. What field do you want to work in?**\n{st.session_state.responses['field_interest']}")
else:
    if st.session_state.step >= 3:
        with st.form(key="form_field"):
            field_interest = st.text_input("What field do you want to work in? (Step 3)")
            submitted = st.form_submit_button("Submit")
            if submitted and field_interest:
                handle_response("field_interest", field_interest)
                st.rerun()  # Force the app to rerun and update the UI

# Final Step: Confirm that answers were collected
if st.session_state.step > 3:
    st.write("Thank you for answering the questions! Let me generate tailored career suggestions for you.")
    
    # Build the prompt based on user inputs
    prompt = f"""
    My major is {st.session_state.responses.get('major', 'not specified')}. 
    My favorite subject is {st.session_state.responses.get('favorite_subject', 'not specified')}. 
    I want to work in {st.session_state.responses.get('field_interest', 'not specified')}.
    Based on this information, suggest three entry-level jobs with reasons, key skills, responsibilities, and requirements.
    """
    image_prompt = f"""
    A young professional working in {st.session_state.responses.get('field_interest', 'a relevant setting')}, 
    with a background in {st.session_state.responses.get('major', 'an unspecified major')} 
    and an interest in {st.session_state.responses.get('favorite_subject', 'various subjects')}. 
    They are engaged in a typical task using relevant tools, wearing professional attire, in a realistic workspace.
    """

    # Generate the AI response
    with st.spinner("Generating career advice..."):
        st.write(get_completion(prompt))
        st.image(get_image(image_prompt))
