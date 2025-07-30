import streamlit as st
import fitz  # PyMuPDF
import os
from openai import OpenAI
from dotenv import load_dotenv
import io
from docx import Document

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# Title and instructions
st.title("AI-Powered Legal PDF Summarizer")
st.markdown("""
Welcome! This tool uses AI to summarize legal PDF documents into clear sections
such as Parties, Effective Date, Obligations, Risk Flags, and more.

**How to use:**
1. Upload a PDF file
2. Wait for the AI to process it
3. Review the summary and download it if needed
""")

# Upload
uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

def extract_text_from_pdf(file):
    text = ""
    pdf = fitz.open(stream=file.read(), filetype="pdf")
    for page in pdf:
        text += page.get_text()
    return text

if uploaded_file:
    st.info("Extracting and summarizing...")
    text = extract_text_from_pdf(uploaded_file)

    prompt = f"""
    Summarize the following legal document under these sections:
    Parties, Effective Date, Term, Confidential Info,
    Obligations, Jurisdiction, Risk Flags.

    Document:
    {text[:10000]}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    # Show the summary
    st.subheader("Summary")
    summary_text = response.choices[0].message.content
    st.write(summary_text)

    # Provide a download button
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
