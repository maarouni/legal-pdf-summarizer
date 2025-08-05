import streamlit as st
import os
import fitz  # PyMuPDF
from openai import OpenAI
from dotenv import load_dotenv
import io
import pandas as pd
from docx import Document

# 🔐 Load environment variables from Streamlit secrets
openai_api_key = st.secrets["OPENAI_API_KEY"]
streamlit_password = st.secrets["STREAMLIT_PASSWORD"]
st.write("🔐 STREAMLIT_PASSWORD loaded:", bool(streamlit_password))

# 🔐 Password Gate
entered_password = st.text_input("🔒 Enter Access Password:", type="password")
if entered_password != streamlit_password:
    st.warning("Please enter the correct password to access the app.")
    st.stop()

# 🔧 Initialize OpenAI client
client = OpenAI(api_key=openai_api_key)

# 🎨 UI Header and Mode Toggle
st.markdown(
    """
    <div style='text-align: center;'>
        <h1>Legal PDF Summarizer</h1>
        <h3 style='margin-top: 0.2em;'>What would you like to do?</h3>
    </div>
    """,
    unsafe_allow_html=True
)

mode = st.radio(
    "",
    ["🟢 🔍 Summarize a Single Document", "🟢 📊 Summarize and Compare Multiple Documents"],
    index=0
)

# 🚀 Start button logic
if st.button("🚀 Start"):
    if "Single" in mode:
        # === SINGLE FILE MODE ===
        uploaded_file = st.file_uploader("Upload a PDF", type="pdf")
        if uploaded_file:
            st.info("Extracting and summarizing...")

            def extract_text_from_pdf(file):
                text = ""
                pdf = fitz.open(stream=file.read(), filetype="pdf")
                for page in pdf:
                    text += page.get_text()

                if pdf.is_form_pdf:
                    text += "\n\nForm Fields:\n"
                    for page in pdf:
                        for widget in page.widgets():
                            field_name = widget.field_name or "UnnamedField"
                            field_value = widget.field_value or ""
                            text += f"{field_name}: {field_value}\n"
                return text

            text = extract_text_from_pdf(uploaded_file)

            prompt = f"""
            Summarize the following legal document with detailed sections.
            If info is missing or unclear, write: "Not specified".

            Sections:
            1. Parties
            2. Effective Date
            3. Term
            4. Confidential Information
            5. Obligations
            6. Jurisdiction
            7. Risk Flags

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
    else:
        # === MULTI FILE MODE ===
        uploaded_files = st.file_uploader("Upload 2–5 PDFs", type="pdf", accept_multiple_files=True)

        if uploaded_files and 2 <= len(uploaded_files) <= 5:
            st.info("Processing documents and comparing...")

            def extract_text(file):
                pdf = fitz.open(stream=file.read(), filetype="pdf")
                return "\n".join(page.get_text() for page in pdf)

            summaries = []
            for file in uploaded_files:
                content = extract_text(file)
                prompt = f"""
                Summarize this legal PDF under the following:
                - Parties
                - Effective Date
                - Expiry or Renewal
                - Jurisdiction
                - Key Obligations
                - Risk Clauses (indemnity, liability, termination)

                If info is missing, write: "Not specified".

                Document:
                {content[:10000]}
                """
                resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}]
                )
                summaries.append(resp.choices[0].message.content)

            df = pd.DataFrame({
                f"Doc {i+1}": summary.split("\n") for i, summary in enumerate(summaries)
            }).T

            st.subheader("🧾 Comparison Table")
            st.dataframe(df)

            csv = df.to_csv().encode("utf-8")
            st.download_button(
                label="📥 Download Comparison as CSV",
                data=csv,
                file_name="comparison.csv",
                mime="text/csv"
            )
        else:
            st.warning("Please upload between 2 and 5 PDF files.")
