import streamlit as st
import os
import fitz  # PyMuPDF
from dotenv import load_dotenv
import io
from docx import Document
from openai import OpenAI

# Load .env secrets
load_dotenv()
st.write("🔐 STREAMLIT_PASSWORD loaded:", bool(os.getenv("STREAMLIT_PASSWORD")))

# Authenticate with Streamlit password
app_password = os.getenv("STREAMLIT_PASSWORD")
entered_password = st.text_input("🔒 Enter Access Password:", type="password")
if entered_password != app_password:
    st.stop()

# Set up OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# Page config
st.set_page_config(page_title="Legal PDF Summarizer", layout="centered")
st.markdown("""
    <div style='text-align: center;'>
        <h1 style='margin-bottom: 0.5em;'>Legal PDF Summarizer</h1>
        <h3 style='margin-top: 0.2em; color: #333;'>What would you like to do?</h3>
    </div>
""", unsafe_allow_html=True)

# Radio Button with Key
st.radio(
    "",
    ["🟢 🔍 Summarize a Single Document", "🟢 📊 Summarize and Compare Multiple Documents"],
    key="mode"
)

# Start button sets a session flag
if st.button("🚀 Start"):
    st.session_state.started = True

# Proceed only if started
if st.session_state.get("started"):
    selected = st.session_state.mode

    if "Single" in selected:
        st.subheader("📄 Upload a PDF")
        file = st.file_uploader("Upload one PDF file", type="pdf")

        if file:
            st.info("Extracting and summarizing...")
            text = ""
            pdf = fitz.open(stream=file.read(), filetype="pdf")
            for page in pdf:
                text += page.get_text()

            prompt = f"""
            Summarize the following legal document into structured sections:
            - Parties, Dates (Effective, Expiry, Renewal)
            - Obligations, Jurisdiction, Risk Flags
            Use bullet points and label missing info as 'Not specified'.

            Document:
            {text[:10000]}
            """

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            summary_text = response.choices[0].message.content
            st.subheader("Summary")
            st.write(summary_text)

            # Downloadable Word summary
            doc = Document()
            doc.add_heading("Legal Document Summary", level=1)
            doc.add_paragraph(summary_text)
            buffer = io.BytesIO()
            doc.save(buffer)
            buffer.seek(0)

            st.download_button(
                label="Download Summary as Word (.docx)",
                data=buffer,
                file_name="summary.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

    elif "Compare" in selected:
        st.subheader("📑 Upload 2–5 PDFs")
        files = st.file_uploader("Upload PDFs for comparison", type="pdf", accept_multiple_files=True)

        if files and 2 <= len(files) <= 5:
            st.success(f"{len(files)} files uploaded. Comparison summarization logic goes here.")
            # Your multi-file logic would go here
        elif files:
            st.warning("Please upload between 2 and 5 PDF files.")
