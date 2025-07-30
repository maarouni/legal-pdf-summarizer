import streamlit as st
import fitz  # PyMuPDF
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

st.title("AI-Powered Legal PDF Summarizer")

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

    st.subheader("Summary")
    st.write(response.choices[0].message.content)
