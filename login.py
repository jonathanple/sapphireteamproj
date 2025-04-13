import streamlit as st
from time import sleep

st.title('Team Sapphire')

employee_id = st.text_input("Employee ID#")
password = st.text_input("Password", type="password")

if st.button("Log in", type="primary"):
    if employee_id == "test" and password == "test":
        st.session_state.logged_in = True
        st.success("Logged in successfully!")
        sleep(0.5)
        st.switch_page("pages/main.py")
    else:
        st.error("Incorrect ID#")
        
        
