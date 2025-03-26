import streamlit as st
import requests
import pandas as pd
import pytesseract
from pdf2image import convert_from_bytes
from io import BytesIO
from PIL import Image
from createEmail import run
import os
import json 
# Backend API URL
API_URL = "http://localhost:8000"

# Sidebar Navigation
st.sidebar.title("📧 AI Email & Document Processor")
page = st.sidebar.radio("Navigate", ["📧 Email & OCR Processing", "📊 Service Requests"])

# 📧 Email & OCR Processing
if page == "📧 Email & OCR Processing":
    st.title("📧 AI-Powered Email & OCR Processing")

    uploaded_email = st.file_uploader("Upload an email file (.EML)", type=["eml"])
    rules = st.text_area("📜 Extraction Rules", "Use email content section only to get the key extracted fields and attachment content section to identify the request types. ")
    request_type_defs = st.text_area("📜 Request Type Definitions", """
            "Adjustment":{
            "Description" : "interest adjustments and loan modifications" , 
            "Sub request types" : []
            },
            "Closing Notice" : {
            "Description" : "Completion or closing of loan" , 
            "Sub request types" : [''Reallocation Fees' ,'Amendment Fees' , ''Reallocation Principal']
            },
            "Commitment Change" : {
            "Description" : "Change of loan commitment" , 
            "Sub request types" : ['Cashless Roll' , 'Decrease' , 'Increase']
            },
            "Fee Payment" : {
            "Description" : "Adjusting money between accounts by an entity" , 
            "Sub request types" : ['Ongoing Fee' , 'Letter of Credit Fee']
            },
            "Money-Movement-inbound" : {
            "Description" : "Wells Fargo Bank receiving money" , 
            "Sub request types" : ['Principal' , 'Interest' , 'Principal + Interest' , 'Principal + Interest + Fee']
            },
            "Money-Movement-outbound" : {
            "Description" : "Wells Fargo bank transferring money to outside entity " , 
            "Sub request types" : ['Timebound' , 'Foreign currency']
            }""")
    extraction_fields = st.text_area("📜 Extraction Fields", """ "date" , "effective date" , "source bank" , "Transactor" , "Amount" , "Expiration Date" , "deal name" """)

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
           

            # Show a loading spinner while processing
            with st.spinner("🔄 Processing the email and generating output..."):
                output = run(file_path, request_type_defs, extraction_fields, rules)
                start_index = output.find("{")
                end_index = output.rfind("}") + 1
                json_content = output[start_index:end_index]
                st.write(json_content)
                # print(json_content)
                # Parse the JSON content
                try:
                    parsed_data = json.loads(json_content)
                    # st.write(parsed_data)
                    # st.write(output[end_index : ])
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON: {e}")
                

            st.success("✅ Processing complete!")
        else:
            st.toast(" Please upload an email file (.EML)", icon="❌")



# 📊 Service Requests Dashboard
elif page == "📊 Service Requests":
    st.title("📊 AI-Powered Service Request Dashboard")
    try: 
        df = pd.read_csv(r"C:\Users\HP\hackathon\gaied-codebenders\code\src\service_requests.csv")
        
        st.dataframe(df)
    except Exception as e :
        st.error(f"❌ Failed to fetch service requests. {e}" )