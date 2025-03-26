import streamlit as st
from time import sleep
# from navigation import make_sidebar

# make_sidebar()

st.title('Team Sapphire')

employee_id = st.text_input("Employee ID#")

if st.button("Log in", type="primary"):
    if employee_id == "test":
        st.session_state.logged_in = True
        st.success("Logged in successfully!")
        sleep(0.5)
        st.switch_page("pages/testpage.py")
    else:
        st.error("Incorrect ID#")
        
        