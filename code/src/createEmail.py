import email
import hashlib
import io
import json
import os
from email import policy
from email.parser import BytesParser
import base64
import os
from google import genai
from pdf2image import convert_from_bytes
import pytesseract
import google as genai
from PIL import Image
# Configure the Gemini API key (from Google AI Studio)

import google.generativeai as genai

# In-memory store for duplicate detection (based on email hash)
PROCESSED_EMAIL_HASHES = set()

class EmailProcessor:
    def __init__(self, raw_email: bytes):
        self.raw_email = raw_email
        self.message = None
        self.subject = ""
        self.from_addr = ""
        self.to_addr = ""
        self.body = ""
        self.attachments = []  # List of tuples: (filename, content bytes)

    def parse_email(self):
        self.message = BytesParser(policy=policy.default).parsebytes(self.raw_email)
        self.subject = self.message.get('subject', '')
        self.from_addr = self.message.get('from', '')
        self.to_addr = self.message.get('to', '')
        if self.message.is_multipart():
            for part in self.message.walk():
                content_type = part.get_content_type()
                disposition = part.get_content_disposition()
                if disposition == 'attachment':
                    filename = part.get_filename()
                    payload = part.get_payload(decode=True)
                    self.attachments.append((filename, payload))
                elif content_type == 'text/plain':
                    self.body += part.get_content()
        else:
            self.body = self.message.get_content()

    def get_email_hash(self) -> str:
        hash_obj = hashlib.sha256()
        hash_obj.update(self.raw_email)
        return hash_obj.hexdigest()

    def get_email_content(self) -> str: 
        return self.body
    
    def extract_text_from_attachment(self, filename: str, content: bytes) -> str:
        """
        Extract text from an attachment.
        Supports PDFs, JPG/JPEG images, and text-based files.
        """
        extracted_text = ""
        lower_filename = filename.lower()
        if lower_filename.endswith(".pdf"):
            try:
                images = convert_from_bytes(content)
                for image in images:
                    extracted_text += pytesseract.image_to_string(image)
            except Exception as e:
                print(f"Error processing PDF attachment {filename}: {e}")
        elif lower_filename.endswith((".jpg", ".jpeg")):
            try:
                # Open image from bytes and extract text with pytesseract.
                image = Image.open(io.BytesIO(content))
                extracted_text = pytesseract.image_to_string(image)
            except Exception as e:
                print(f"Error processing image attachment {filename}: {e}")
        elif lower_filename.endswith((".txt", ".csv", ".json")):
            try:
                extracted_text = content.decode('utf-8')
            except Exception as e:
                print(f"Error decoding attachment {filename}: {e}")
        else:
            # Extend with other file types if needed.
            extracted_text = ""
        return extracted_text

# ------------------------------------------------------------------------------
# Function to call the LLM with all necessary inputs.
def call_llm_for_processing(email_text: str, attachment_text: str,
                            rules: str, request_type_defs: str,
                     extraction_fields:list ) -> dict:
    input = f"""
  
    rules: {rules},
    extraction_fields: {extraction_fields} , 
    Email Content:
    {email_text}

    Attachment content:
    {attachment_text}

    Rules:
    {json.dumps(rules, indent=2)}

    Request type description:
    {json.dumps(request_type_defs, indent=2)}

    
    """
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])

    # Create the model
    generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
    model_name="tunedModels/finetunedgemini25proexp0325-nwk0346634no",
    generation_config=generation_config,
    )

    chat_session = model.start_chat(
    history=[
    ]
    )

    response = chat_session.send_message(input)

    return response 

# ------------------------------------------------------------------------------
# Main processing function which ties everything together.
def process_email_with_llm(raw_email: bytes , request_type_defs: str,extraction_fields : list, rules:str ="Use email content section only to get the key extracted fields and attachment content section to identify the request types."  ) -> dict:
    """
    Process a raw email by:
      1. Parsing the email and attachments.
      2. Checking for duplicates.
      3. Combining email body and attachment texts (based on user-defined priority).
      4. Calling the LLM (e.g., Google Gemini) to obtain request type classification,
         extracted fields, and duplicate detection details.
    Returns a dictionary with metadata and the LLM output.
    """
    processor = EmailProcessor(raw_email)
    processor.parse_email()
    
    email_hash = processor.get_email_hash()
    if email_hash in PROCESSED_EMAIL_HASHES:
        print("Email already present" )
        duplicate_info = {"flag": True, "reason": f"Duplicate email detected based on hash: {email_hash}"}
        print("Duplicate email detected") 
        return
    else:
        PROCESSED_EMAIL_HASHES.add(email_hash)
        duplicate_info = {"flag": False, "reason": "Unique email hash"}
    
    attachment_texts = ""
    for filename, content in processor.attachments:
        attachment_texts += f"\n--- Text from {filename} ---\n"
        attachment_texts += processor.extract_text_from_attachment(filename, content)
    
         
         
    # Combine email body and attachment texts based on the defined priority.
    email_text = processor.get_email_content() 
    output = call_llm_for_processing(email_text=email_text , attachment_text=attachment_texts, rules=rules, request_type_defs=request_type_defs, extraction_fields=extraction_fields)
    # Call the LLM to process and interpret the content.
    
    return output


'''
input : 

Email - in .eml format 
request_type_defs - dictionary with the request type definitions , 
extraction_fields - list of fields to be extracted from the email , 
rules - rules to be applied for the extraction of the fields. 
'''

def main():

    rules = "Use email content section only to get the key extracted fields and attachment content section to identify the request types. "

    extraction_fields= [ "date" , "effective date" , "source bank" , "Transactor" , "Amount" , "Expiration Date" , "deal name" ]

    request_type_defs = """
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
        }"""

    # Attempt to load an email from a file; if not found, use simulated content.
    try:
        with open(r"C:\Users\HP\hackathon\gaied-codebenders\Order.eml", "rb") as f:
            raw_email = f.read()
    except Exception as e :  
        print(f"Error loading email file: {e}")
        return 
    
    result = process_email_with_llm(raw_email,  request_type_defs, extraction_fields, rules)
    print(json.dumps(result, indent=4))

if __name__ == "__main__":
    main()
