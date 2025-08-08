import os
import time
import streamlit as st
import PyPDF2
from openai import OpenAI
import pandas as pd
import re

# Load secrets
PASSWORD_SECRET = st.secrets["STREAMLIT_PASSWORD"]
OPENAI_KEY = st.secrets["OPENAI_API_KEY"]

# Set up page
st.set_page_config(page_title="Legal PDF Summarizer")
st.title("📄 Legal PDF Summarizer")

# Password gate
password = st.text_input("Enter app password:", type="password")
if not password:
    st.stop()
if password != PASSWORD_SECRET:
    st.error("❌ Incorrect password")
    st.stop()

# Mode selection menu
mode = st.radio(
    "What would you like to do?",
    ["🔍 Summarize a Single Document", "📊 Summarize and Compare Multiple Documents"]
)

# PDF text extraction helper
def extract_pdf_text(file):
    reader = PyPDF2.PdfReader(file)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() or ""
    return full_text.strip()

# === CHUNKING DISABLED: Summarization function without chunking ===
def summarize_text(text):
    client = OpenAI(api_key=OPENAI_KEY)
    model = "gpt-4o-mini"

    try:
        with st.spinner("🧠 Summarizing entire document..."):
            final = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a precise legal contract summarizer."},
                    {"role": "user", "content": (
                        "For the given text, produce a structured summary with these sections:\n"
                        "1. Parties\n2. Effective Date\n3. Term\n4. Confidential Information\n"
                        "5. Obligations\n6. Jurisdiction\n7. Risk Flags\n\n"
                        f"Text:\n{text}"
                    )}
                ],
                temperature=0.2,
                max_tokens=1500
            )
        return final.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Summarization failed: {e}"

# === Main Logic ===
if mode == "🔍 Summarize a Single Document":
    uploaded_file = st.file_uploader("Upload a legal PDF", type=["pdf"])
    if uploaded_file:
        pdf_text = extract_pdf_text(uploaded_file)
        if not pdf_text:
            st.warning("⚠️ The uploaded PDF appears to be empty.")
        else:
            try:
                with st.spinner("🧠 Summarizing document..."):
                    summary_output = summarize_text(pdf_text)
                st.subheader("📄 Summary Output")
                st.write(summary_output)
            except Exception as e:
                st.error(f"❌ Error during summarization:\n\n{e}")

elif mode == "📊 Summarize and Compare Multiple Documents":
    uploaded_files = st.file_uploader("Upload multiple legal PDFs", type=["pdf"], accept_multiple_files=True)

    if uploaded_files:
        summaries = {}
        for file in uploaded_files:
            text = extract_pdf_text(file)
            if text:
                try:
                    with st.spinner(f"Summarizing {file.name}..."):
                        summary = summarize_text(text)
                        summaries[file.name] = summary
                except Exception as e:
                    summaries[file.name] = f"❌ Error: {e}"
            else:
                summaries[file.name] = "⚠️ Empty or unreadable file."

        # Display comparison table
        st.subheader("📊 Comparison Table")

        sections = [
            "Parties",
            "Effective Date",
            "Term",
            "Confidential Information",
            "Obligations",
            "Jurisdiction",
            "Risk Flags"
        ]

        def extract_section(summary_text, section_name):
            pattern = rf"{section_name}.*?:([\s\S]*?)(?=\n[A-Z][a-z]+:|\n[A-Z][A-Z ]+:|$)"
            match = re.search(pattern, summary_text, re.IGNORECASE)
            return match.group(1).strip() if match else "Not specified"

        comparison_data = {section: [] for section in sections}
        file_labels = []

        for filename, summary in summaries.items():
            file_labels.append(filename)
            for section in sections:
                content = extract_section(summary, section)
                comparison_data[section].append(content)

        df = pd.DataFrame(comparison_data, index=file_labels)

        if not df.empty:
            st.dataframe(df.transpose())
        else:
            st.warning("⚠️ Could not extract structured sections from one or more summaries.")

        # Always show raw summaries below as fallback
        st.subheader("🗂 Raw Summary Comparison")
        for filename, summary in summaries.items():
            with st.expander(f"📄 {filename}"):
                st.markdown(summary)