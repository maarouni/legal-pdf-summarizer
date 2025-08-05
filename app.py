import streamlit as st
import os
from dotenv import load_dotenv
import fitz  # PyMuPDF
import pandas as pd

# Set Streamlit page config
st.set_page_config(page_title="Legal PDF Summarizer", layout="centered")

# Load environment variables
load_dotenv()

# ✅ Diagnostic line to confirm secret is being loaded
st.write("🔐 STREAMLIT_PASSWORD loaded:", bool(os.getenv("STREAMLIT_PASSWORD")))

# Password Gate
correct_password = os.getenv("STREAMLIT_PASSWORD")
entered_password = st.text_input("🔒 Enter Access Password:", type="password")

if entered_password != correct_password:
    st.warning("Please enter the correct password to access the app.")
    st.stop()

# UI Header
st.markdown(
    """
    <div style='text-align: center;'>
        <h1 style='margin-bottom: 0.5em;'>Legal PDF Summarizer</h1>
        <h3 style='margin-top: 0.2em; color: #333;'>What would you like to do?</h3>
    </div>
    """,
    unsafe_allow_html=True
)

# App mode selection
mode = st.radio(
    "",
    ["🟢 🔍 Summarize a Single Document", "🟢 📊 Summarize and Compare Multiple Documents"],
    index=0,
)

# Start Button
if st.button("🚀 Start"):
    if "Single" in mode:
        st.success("Launching single document summarizer... ⏳")
        os.system("streamlit run app_single_file.py")
    else:
        st.success("Launching multi-file summarizer and comparer... ⏳")
        os.system("streamlit run app_multi_file.py")
