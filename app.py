import streamlit as st
import fitz  # PyMuPDF
import os
import pandas as pd
import io
from docx import Document
from openai import OpenAI
from dotenv import load_dotenv

# Load .env (for local dev)
load_dotenv()

# ✅ Load secrets (Streamlit Cloud or local fallback)
openai_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
streamlit_pwd = os.getenv("STREAMLIT_PASSWORD") or st.secrets.get("STREAMLIT_PASSWORD")

# 🔐 Password Gate
st.write("🔐 STREAMLIT_PASSWORD loaded:", bool(streamlit_pwd))
entered_password = st.text_input("🔒 Enter Access Password:", type="password")
if entered_password != streamlit_pwd:
    st.warning("Please enter the correct password to access the app.")
    st.stop()

# Set OpenAI client
client = OpenAI(api_key=openai_key)

# UI Layout
st.markdown(
    """
    <div style='text-align: center;'>
        <h1 style='margin-bottom: 0.5em;'>Legal PDF Summarizer</h1>
        <h3 style='margin-top: 0.2em; color: #333;'>What would you like to do?</h3>
    </div>
    """,
    unsafe_allow_html=True
)

mode = st.radio(
    "",
    ["🟢 🔍 Summarize a Single Document", "🟢 📊 Summarize and Compare Multiple Documents"]
)

start_clicked = st.button("🚀 Start")

# --- Functions ---
def extract_text(file):
    text = ""
    pdf = fitz.open(stream=file.read(), filetype="pdf")
    for page in pdf:
        text += page.get_text()
    return text

def summarize_text(text, model="gpt-4o-mini"):
    prompt = f"""
    Summarize the following legal document with detailed sections.
    If any section is missing, write "Not specified".

    Sections:
    1. Parties
    2. Effective Date
    3. Term
    4. Confidential Info
    5. Obligations
    6. Jurisdiction
    7. Risk Flags

    Document:
    {text[:10000]}
    """
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def show_download_button(content, filename="summary.docx"):
    doc = Document()
    doc.add_heading("Legal Document Summary", level=1)
    doc.add_paragraph(content)
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    st.download_button(
        label="Download Summary as Word (.docx)",
        data=buffer,
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

# --- Main Logic ---
if start_clicked:
    if "Single" in mode:
        st.subheader("Upload a PDF")
        uploaded_file = st.file_uploader("Choose a legal PDF", type="pdf")
        if uploaded_file:
            with st.spinner("Summarizing document..."):
                text = extract_text(uploaded_file)
                summary = summarize_text(text)
                st.subheader("📄 Summary")
                st.write(summary)
                show_download_button(summary)

    else:
        st.subheader("Upload 2–5 PDFs")
        uploaded_files = st.file_uploader("Choose multiple PDFs", type="pdf", accept_multiple_files=True)
        if uploaded_files:
            if not (2 <= len(uploaded_files) <= 5):
                st.warning("Please upload between 2 and 5 PDF files.")
            else:
                summaries = []
                with st.spinner("Summarizing all documents..."):
                    for file in uploaded_files:
                        text = extract_text(file)
                        summary = summarize_text(text)
                        summaries.append((file.name, summary))

                st.subheader("📊 Comparison Table")
                for filename, summary in summaries:
                    with st.expander(f"📄 {filename}"):
                        st.write(summary)
                # Optional export logic can go here
