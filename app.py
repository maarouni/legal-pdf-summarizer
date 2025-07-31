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
such as Parties, Dates, Obligations, Jurisdiction, and Risk Flags.

**How to use:**
1. Upload a PDF file (NDA, contract, policy, etc.)
2. Wait for the AI to process it
3. Review the structured summary and download it if needed
""")

def extract_text_from_pdf(file):
    text = ""
    pdf = fitz.open(stream=file.read(), filetype="pdf")
    for page in pdf:
        text += page.get_text()
    return text

# Layout: two columns
col1, col2 = st.columns([1, 2])

with col1:
    uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

with col2:
    if uploaded_file:
        st.info("Extracting and summarizing...")
        text = extract_text_from_pdf(uploaded_file)

        # Enhanced prompt with explicit "Not specified" requirement
        prompt = f"""
        Summarize the following legal document with detailed sections.
        For any section where the information is missing or not clearly stated,
        explicitly write: "Not specified".

        Sections to include:

        1. Parties:
            - All entities and individuals involved.
        2. Effective Date:
            - Start date of the agreement
            - End date/expiry (if mentioned)
            - Renewal terms (if applicable)
        3. Term:
            - Duration of the agreement.
        4. Confidential Information:
            - Definitions
            - Restrictions
        5. Obligations:
            - Key duties of each party
            - Payment terms, deliverables, deadlines
        6. Jurisdiction:
            - Governing law
            - Venue/courts
        7. Risk Flags:
            - Liabilities
            - Termination conditions
            - Indemnities
            - Any unusual or one-sided clauses

        Provide the output as structured bullet points with sub-bullets.

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
