import docx.document
from flask import Flask, request, jsonify
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
import json, re, os, io
from dotenv import load_dotenv
from prompts import system_prompt
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader  # For PDF parsing
import docx 
# from pdf2image import convert_from_bytes
import pytesseract
from PIL import Image
import fitz
from flask_cors import CORS


app =Flask(__name__)
# CORS(app)  # <-- enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "*"}})


#to use API key from .env
load_dotenv()

API_KEY = os.getenv("My_API_KEY")

#ai model name
MODEL_NAME = "llama3-8b-8192"


#extract json from text
def extract_json_from_text(text):
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        return match.group()
    return None


def extract_text_from_pdf(file_stream): #for PDF files 
    try:
        reader = PdfReader(file_stream)
        texts = []
        for pages in reader.pages:
            page_text = pages.extract_text()
            if page_text:
                texts.append(page_text)
        return '\n'.join(texts)
    except Exception as e:
        return " "

def extract_text_from_docx(file_stream):
    try:
        doc = docx.Document(file_stream)
        return '\n'.join([para.text for para in doc.paragraphs])
    except Exception as e:
        return " "

def extract_text_from_scanned_pdf_with_fitz(file_bytes):
    try:
        pdf = fitz.open(stream=file_bytes, filetype="pdf")
        extracted_text = ""
        for page in pdf:
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            text = pytesseract.image_to_string(img)
            extracted_text += text + "\n"
        return extracted_text.strip()
    except Exception as e:
        return ""
    
def extract_text_from_image(image_file):
    try:        
        image = Image.open(image_file)
        return pytesseract.image_to_string(image).strip()
    except Exception as e:
        return " "

#api route
@app.route('/', methods=['POST'])
def diagnosis_prediction():
    
    symptoms = request.form.get('symptoms', '').strip()
    age = request.form.get('age')
    gender = request.form.get('gender', '').strip().lower()
    existing_conditions = request.form.get('existing_conditions', '').strip() #optional
    report_file = request.files.get('report_file')  #optional
    
    # print("DEBUG - Received:")
    # print("Symptoms:", symptoms)
    # print("Age:", age)
    # print("Gender:", gender)
    # print("Existing Conditions:", existing_conditions)
    # print("Report file:", report_file.filename if report_file else "None")

    if not symptoms or not age or not gender:
        return jsonify({"error": "Please provide the symptoms, age, and gender, all fields are required for better prediction"}), 400

    report_content = ""
     
    if report_file:
        file_name = report_file.filename.lower()
        
        #for handling PDF files
        if file_name.endswith('.pdf'):
            file_bytes = report_file.read()
            report_content = extract_text_from_pdf(io.BytesIO(file_bytes))
            if not report_content.strip():
                report_content = extract_text_from_scanned_pdf_with_fitz(file_bytes)
            
        #docx handling
        elif file_name.endswith('.docx'):
            report_content = extract_text_from_docx(report_file.stream)
            
        #Image Handling
        elif file_name.endswith(('.jpg','.png','.jpeg')):
            report_content = extract_text_from_image(report_file)
           
        else:
            return jsonify({"error":"Supported file formats are .pdf, .docx, .jpg, .png, .jpeg"}), 400
                
    
    #Construct the combined prompt for AI model
    combined_prompt = (
        f"Patient details:\n"
        f"age: {age}\n"
        f"gender: {gender}\n"
        f"symptoms: {symptoms}\n"
        f"existing conditions: {existing_conditions}\n"
    )
    
    if report_content:
        combined_prompt += f"\nReport content:\n{report_content.strip()}"
    
    try:
        chat_client = ChatGroq(
            model = MODEL_NAME,
            api_key = API_KEY,
            temperature=0.7,
            timeout=30 # wait for up to 30 seconds for a response
        )
        message = [
            SystemMessage(content=system_prompt["manual"]),
            HumanMessage(content=combined_prompt)
        ]
        
        ai_response = chat_client.invoke(message)
        
        if ai_response and hasattr(ai_response, 'content'):
            response_content_str = ai_response.content.strip()
            # app.logger.info(f"Raw AI response content:{response_content_str}")
            
            try:
                cleaned_json = extract_json_from_text(response_content_str)
                if cleaned_json:
                    parsed_json_response = json.loads(cleaned_json)
                    return jsonify(parsed_json_response), 200
                else:
                #     app.logger.error(f"Failed to extract JSON from response: {response_content_str}")
                # return jsonify({"error": "AI response did not contain valid JSON"}), 500
                
                
                # This is a fallback. It triggers if the AI, despite the prompt,
                # returns a plain text message for irrelevant input instead of JSON.
                    app.logger.warning(f"AI did not return JSON. Raw Response: {response_content_str}. Creating a fallback JSON response")
                #Manully create the structured JSON response for invalid input
                    fallback_response = {
                        "diagnosis": "Invalid Input",
                        "prescription": [],
                        "duration": "",
                        "tests": [],
                        "safety": "",
                        "Do and Don'ts": { "Do": [], "Don't": [] },
                        "Note": "The information provided was not recognized as a valid medical query. Please provide relevant symptoms for an accurate diagnosis."
                    }
                    return jsonify(fallback_response), 200
                
                
            except json.JSONDecodeError as e:
                app.logger.error(f"JSON decoding error: {e}  --Raw Response : {response_content_str}")
                return jsonify({"error": "Invalid JSON response from AI"}), 500   
        else:
            app.logger.error(f"AI response is empty or invalid: {ai_response}")
            return jsonify({"error": "AI response is empty or invalid"}), 500
        
    except Exception as e:
        # catch any unexpected errors
        app.logger.error(f"Error occurred: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(debug=True)