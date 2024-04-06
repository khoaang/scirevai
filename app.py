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


def extract_text_from_pdf(file):
    try:
        # Save the file temporarily
        file.save("temp.pdf")

        # Convert PDF to images
        images = convert_from_path("temp.pdf")

        text = ''
        for image in images:
            text += pytesseract.image_to_string(image)

        # Remove the temporary file
        os.remove("temp.pdf")

        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None


def generate_response(text):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are Dr. GPT, a prestigious scientific proposal reviewer, and a Chair at the GPT Funding for Sciences. Establish an academic tone. Analyze the problem statement, the goals, methods, and scrutinize the budget and justification.Be holistic and harsh and ensure it meets requirements to be a likely to be approved grant proposal."},
            {"role": "system", "content": "In a formal letter response format, Be sure to address the author by name and provide a detailed critique of the proposal. Be sure to include both positive and negative feedback. Be formal and professional in your response."},
            {"role": "system", "content": "If the proposal is clearly subpar, do not be afraid to go all out. There is no such thing as being rude. Please include line breaks between your responses to make it easier to read."},

            {"role": "assistant", "content": text}
        ],
        max_tokens=1000,
    )
    print(response)
    return response.choices[0].message.content


if __name__ == '__main__':
    app.run(debug=True)
