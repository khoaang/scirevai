from flask import render_template
from flask import Flask, request, jsonify
from pypdf import PdfReader
from openai import OpenAI
from dotenv import load_dotenv
import os
from pdf2image import convert_from_path
import pytesseract

load_dotenv()  # Load environment variables
app = Flask(__name__)
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)


@ app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@ app.route('/upload', methods=['POST'])
def upload_pdf():
    print('Uploading PDF')
    if 'pdf' not in request.files:
        return "PDF file is required.", 400
    file = request.files['pdf']
    if file.filename == '':
        return "No file selected.", 400

    # Extract text from PDF
    text = extract_text_from_pdf(file)
    if not text:
        return "Failed to extract text from PDF.", 400

    # Generate GPT-3.5 response
    response = generate_response(text)
    return jsonify({"response": response})

import uuid

from pypdf import PdfReader
import uuid

def extract_text_from_pdf(file):
    try:
        # Generate a unique filename
        filename = f"{uuid.uuid4()}.pdf"

        # Save the file temporarily
        file.save(filename)

        # Extract text from PDF
        reader = PdfReader(filename)
        text = ''
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text is not None:
                text += page_text
        if not text:
            print("No text extracted from PDF.")
            return None

        # Remove the temporary file
        os.remove(filename)

        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None
    finally:
        # Remove the temporary file if it still exists
        if os.path.exists(filename):
            os.remove(filename)

def extract_text_from_pdf_as_image(file):
    try:
        # Generate a unique filename
        filename = f"{uuid.uuid4()}.pdf"

        # Save the file temporarily
        file.save(filename)

        # Convert PDF to images
        images = convert_from_path(filename)
        text = ''
        for image in images:
            text += pytesseract.image_to_string(image)

        # Remove the temporary file
        os.remove(filename)

        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None
    finally:
        # Remove the temporary file if it still exists
        if os.path.exists(filename):
            os.remove(filename)

def generate_response(text):
    # get system prompt from file "system_prompt.txt"
    prompt = open("system_prompt.txt", "r").read()
    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "assistant", "content": text}
        ],
        max_tokens=1000,
    )
    print(response)
    return response.choices[0].message.content


if __name__ == '__main__':
    app.run(debug=True)