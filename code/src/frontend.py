import streamlit as st
import requests
import pandas as pd
import pytesseract
from pdf2image import convert_from_bytes
from io import BytesIO
from PIL import Image
from createEmail import run
import os

# Backend API URL
API_URL = "http://localhost:8000"

# Sidebar Navigation
st.sidebar.title("📧 AI Email & Document Processor")
page = st.sidebar.radio("Navigate", ["📧 Email & OCR Processing", "📊 Service Requests"])

# 📧 Email & OCR Processing
if page == "📧 Email & OCR Processing":
    st.title("📧 AI-Powered Email & OCR Processing")

    uploaded_email = st.file_uploader("Upload an email file (.EML)", type=["eml"])
    rules = st.text_area("📜 Extraction Rules", "Please enter the extraction rules here...")
    request_type_defs = st.text_area("📜 Request Type Definitions", "Please enter the request type definitions here...")
    extraction_fields = st.text_area("📜 Extraction Fields", "Please enter the extraction fields here...")

    email_content = ""
    extracted_text = ""


    if st.button("🔍 Process Email & OCR"):
        if uploaded_email and rules and request_type_defs and extraction_fields:
            # Save the uploaded file to a temporary location
            temp_dir = "temp_uploads"
            os.makedirs(temp_dir, exist_ok=True)  # Create the directory if it doesn't exist
            file_path = os.path.join(temp_dir, uploaded_email.name)

            with open(file_path, "wb") as f:
                f.write(uploaded_email.getbuffer())  # Write the file content to the local file

            st.success(f"File saved to: {file_path}")
            st.write(f"File path: {file_path}")

            # Show a loading spinner while processing
            with st.spinner("🔄 Processing the email and generating output..."):
                output = run(file_path, request_type_defs, extraction_fields, rules)
                print(output)
                st.write(output)

            st.success("✅ Processing complete!")
        else:
            st.toast("❌ Please upload an email file (.EML)", icon="warning")



# 📊 Service Requests Dashboard
elif page == "📊 Service Requests":
    st.title("📊 AI-Powered Service Request Dashboard")
    response = requests.get(f"{API_URL}/service-requests")
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)
        st.dataframe(df)
    else:
        st.error("❌ Failed to fetch service requests.")