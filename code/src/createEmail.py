import email
import hashlib
import io
import json
from email import policy
from email.parser import BytesParser

# For PDF to image conversion
try:
    from pdf2image import convert_from_bytes
except ImportError:
    print("pdf2image not installed. PDF OCR functions will not work.")

# For image processing
try:
    from PIL import Image
except ImportError:
    print("Pillow not installed. Image OCR functions will not work.")

# Optional: For additional NLP extraction (e.g., using spaCy)
try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
except Exception as e:
    print("spaCy or en_core_web_sm not installed. NLP-based extraction will be limited.", e)
    nlp = None

# In-memory store for duplicate detection based on email hash.
PROCESSED_EMAIL_HASHES = set()

# ------------------------------------------------------------------------------
# Function to call Gemma 3 for OCR using a Hugging Face transformers pipeline.
def gemma3_ocr(image_bytes: bytes, filename: str) -> str:
    """
    Use Gemma 3 to extract text from an image.
    This function initializes an image-to-text pipeline using Gemma 3.
    """
    from transformers import pipeline
    try:
        ocr_pipeline = pipeline("image-to-text", model="google/gemma-3-12b-it", device=0)
    except Exception as e:
        print("Error initializing Gemma 3 OCR pipeline:", e)
        return ""
    
    try:
        image = Image.open(io.BytesIO(image_bytes))
    except Exception as e:
        print(f"Error opening image for {filename}: {e}")
        return ""
    
    try:
        result = ocr_pipeline(image)
        extracted = result[0]["generated_text"] if result and "generated_text" in result[0] else ""
        return extracted
    except Exception as e:
        print(f"Error processing OCR for {filename}: {e}")
        return ""

# ------------------------------------------------------------------------------
# Function to prompt Gemma 3 for a final response.
def prompt_gemma3_response(prompt: str) -> str:
    """
    Use Gemma 3 to generate a text response from a given prompt.
    """
    from transformers import pipeline
    try:
        generation_pipeline = pipeline("text-generation", model="google/gemma-3-12b-it", device=0)
    except Exception as e:
        print("Error initializing Gemma 3 text generation pipeline:", e)
        return ""
    
    try:
        result = generation_pipeline(prompt, max_new_tokens=200)
        return result[0]["generated_text"]
    except Exception as e:
        print("Error generating response with Gemma 3:", e)
        return ""

# ------------------------------------------------------------------------------
# Function to call Gemma 3 for classification/extraction.
def gemma3_classification_response(prompt: str) -> dict:
    """
    Uses Gemma 3 to process a prompt that requests classification and extraction,
    expecting the output in JSON format.
    """
    response_text = prompt_gemma3_response(prompt)
    try:
        # Attempt to parse the output as JSON.
        response_json = json.loads(response_text)
    except Exception as e:
        print("Error parsing Gemma 3 classification response as JSON:", e)
        # If parsing fails, return the raw text wrapped in a dict.
        response_json = {"raw_response": response_text}
    return response_json

# ------------------------------------------------------------------------------
# Helper to build final prompt and generate a final response.
def generate_final_response(context: str, query: str) -> str:
    """
    Combines the OCR extracted email content and attachments with a final query,
    and uses Gemma 3 to generate a response.
    """
    prompt = (f"Based on the following email and attachment content:\n\n{context}\n\n"
              f"Answer the following question succinctly:\n{query}\n")
    response_text = prompt_gemma3_response(prompt)
    return response_text

# ------------------------------------------------------------------------------
# Email Processing Class
class EmailProcessor:
    def __init__(self, raw_email: bytes):
        self.raw_email = raw_email
        self.message = None
        self.subject = None
        self.from_addr = None
        self.to_addr = None
        self.body = ""
        self.attachments = []  # list of (filename, content bytes)
    
    def parse_email(self):
        """
        Parse the raw email into its components: subject, sender, recipient,
        body text, and attachments.
        """
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
        """
        Generate a SHA256 hash of the raw email for duplicate detection.
        """
        hash_obj = hashlib.sha256()
        hash_obj.update(self.raw_email)
        return hash_obj.hexdigest()
    
    def extract_text_from_attachment(self, filename: str, content: bytes) -> str:
        """
        Extract text from an attachment.
        Uses Gemma 3 OCR for PDFs and image files (jpg, jpeg, png),
        and decodes text-based files.
        """
        extracted_text = ""
        lower_filename = filename.lower()
        if lower_filename.endswith(".pdf"):
            try:
                images = convert_from_bytes(content)
                for image in images:
                    buffer = io.BytesIO()
                    image.save(buffer, format="PNG")
                    image_bytes = buffer.getvalue()
                    extracted_text += gemma3_ocr(image_bytes, filename) + "\n"
            except Exception as e:
                print(f"Error processing PDF attachment {filename}: {e}")
        elif lower_filename.endswith((".jpg", ".jpeg", ".png")):
            try:
                extracted_text = gemma3_ocr(content, filename)
            except Exception as e:
                print(f"Error processing image attachment {filename}: {e}")
        elif lower_filename.endswith((".txt", ".csv", ".json")):
            try:
                extracted_text = content.decode('utf-8')
            except Exception as e:
                print(f"Error decoding attachment {filename}: {e}")
        else:
            extracted_text = ""
        return extracted_text

# ------------------------------------------------------------------------------
# Function to call Gemma 3 for classification/extraction based on email content.
def call_classification_with_gemma3(email_text: str, attachment_text: str,
                                    rules: dict, request_type_defs: dict,
                                    duplicate_info: dict) -> dict:
    """
    Build a prompt that includes email content, attachment text, rules, and request type
    definitions, along with duplicate detection info. Use Gemma 3 to output a JSON response.
    """
    prompt = f"""Process the following email content and attachment text using the provided rules and request type definitions.

Email Content:
{email_text}

Attachment Text:
{attachment_text}

Rules:
{json.dumps(rules, indent=2)}

Request Type Definitions:
{json.dumps(request_type_defs, indent=2)}

Duplicate Info:
{json.dumps(duplicate_info, indent=2)}

Output a JSON with the following structure:
{{
  "request_types": [
    {{"type": "Request type name", "priority": "High/Medium/Low", "confidence": 0.0-1.0}},
    ...
  ],
  "extracted_fields": {{
      "field1": "value1",
      "field2": "value2",
      ...
  }},
  "duplicate": {{
      "flag": true/false,
      "reason": "Reason for duplicate classification"
  }}
}}
"""
    return gemma3_classification_response(prompt)

# ------------------------------------------------------------------------------
# Main processing function which ties everything together.
def process_email_with_gemma3(raw_email: bytes, rules: dict, request_type_defs: dict,
                              priority: str = "email", final_query: str = None) -> dict:
    """
    Process a raw email by:
      1. Parsing the email and attachments.
      2. Checking for duplicates.
      3. Combining email body and attachment texts (based on user-defined priority).
      4. Calling Gemma 3 for classification and extraction.
      5. (Optional) Prompting Gemma 3 to generate a final response based on a query.
    Returns a dictionary with metadata, the classification output, and the final Gemma 3 response if requested.
    """
    processor = EmailProcessor(raw_email)
    processor.parse_email()
    
    email_hash = processor.get_email_hash()
    if email_hash in PROCESSED_EMAIL_HASHES:
        duplicate_info = {"flag": True, "reason": f"Duplicate email detected based on hash: {email_hash}"}
    else:
        PROCESSED_EMAIL_HASHES.add(email_hash)
        duplicate_info = {"flag": False, "reason": "Unique email hash"}
    
    attachment_texts = ""
    for filename, content in processor.attachments:
        attachment_texts += f"\n--- Text from {filename} ---\n"
        attachment_texts += processor.extract_text_from_attachment(filename, content)
    
    if priority == "email":
        combined_text = processor.body + "\n" + attachment_texts
    else:
        combined_text = attachment_texts + "\n" + processor.body
    
    classification_output = call_classification_with_gemma3(processor.body, attachment_texts, rules, request_type_defs, duplicate_info)
    
    final_response = ""
    if final_query:
        final_response = generate_final_response(combined_text, final_query)
    
    output = {
        "subject": processor.subject,
        "from": processor.from_addr,
        "to": processor.to_addr,
        "classification_output": classification_output,
        "raw_body": processor.body,
        "attachments": [fname for fname, _ in processor.attachments],
        "final_response": final_response
    }
    return output

# ------------------------------------------------------------------------------
# Example usage demonstrating the complete flow.
def main():
    # Define rules and request type definitions.
    rules = {
        "priority_rule": "If email body contains key phrases, prioritize email content over attachments for numerical fields.",
        "multi_request_rule": "If multiple request types are detected, select the primary based on the highest confidence score."
    }
    
    request_type_defs = {
        "Loan Modification Request": {"description": "Request to modify loan terms."},
        "Payment Extension": {"description": "Request to extend payment due dates."},
        "General Inquiry": {"description": "General questions or requests."}
    }
    
    # Sample email 1: a text-based email.
    raw_email_1 = b"""From: sender@example.com
To: service@example.com
Subject: Request for Loan Modification

Hello Team,

I would like to request a loan modification for loan ID 123456.
The amount in question is 25000 USD, and I would appreciate an extension until 2025-04-15.

Thank you,
Customer A
"""
    # Sample email 2: an email with attachments (text and image simulation).
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.application import MIMEApplication
    from email.mime.image import MIMEImage
    
    message = MIMEMultipart()
    message["From"] = "sender2@example.com"
    message["To"] = "service@example.com"
    message["Subject"] = "Multiple Requests: Payment Extension and Document Submission"
    body_text = "Dear Team,\n\nPlease find the details of my payment extension request attached."
    message.attach(MIMEText(body_text, "plain"))
    
    # Simulate a text attachment.
    attachment_text = "Loan ID: 789012\nRequested extension date: 2025-05-30\nAmount: 15000 USD"
    attachment_part = MIMEApplication(attachment_text.encode('utf-8'), Name="request_details.txt")
    attachment_part['Content-Disposition'] = 'attachment; filename="request_details.txt"'
    message.attach(attachment_part)
    
    # Simulate an image attachment (if available, ensure 'sample_image.jpg' exists).
    try:
        with open("sample_image.jpg", "rb") as img_file:
            image_content = img_file.read()
        image_part = MIMEImage(image_content, _subtype="jpeg")
        image_part.add_header('Content-Disposition', 'attachment', filename="sample_image.jpg")
        message.attach(image_part)
    except Exception as e:
        print("sample_image.jpg not found. Skipping image attachment simulation.", e)
    
    raw_email_2 = message.as_bytes()
    
    emails = [raw_email_1, raw_email_2]
    results = []
    # Define a final query to ask Gemma 3 (e.g., summarize and extract key request details).
    final_query = "Please summarize the email content and provide the main request details."
    
    for raw_email in emails:
        result = process_email_with_gemma3(raw_email, rules, request_type_defs, priority="email", final_query=final_query)
        if result:
            results.append(result)
    
    import json
    print(json.dumps(results, indent=4))

if __name__ == "__main__":
    main()
