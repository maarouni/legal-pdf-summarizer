import streamlit as st
import os

st.set_page_config(page_title="Legal PDF Summarizer", layout="centered")

# Title Section (clean, centered, no duplication)
st.markdown(
    """
    <div style='text-align: center;'>
        <h1 style='margin-bottom: 0.5em;'>Legal PDF Summarizer</h1>
        <h3 style='margin-top: 0.2em; color: #333;'>What would you like to do?</h3>
    </div>
    """,
    unsafe_allow_html=True
)

# Radio Button Selection
mode = st.radio(
    "",
    ["🟢 🔍 Summarize a Single Document", "🟢 📊 Summarize and Compare Multiple Documents"],
    index=0,
)

# Launch Button
if st.button("🚀 Start"):
    if "Single" in mode:
        st.success("Launching single document summarizer... ⏳")
        os.system("streamlit run app.py")
    else:
        st.success("Launching multi-file summarizer and comparer... ⏳")
        os.system("streamlit run app_multi_file.py")
