from flask import Flask, request, jsonify, send_file
from fpdf import FPDF
import os
from flask_cors import CORS
import openai

app = Flask(__name__)
CORS(app)

# OpenAI API Key (Set this as an environment variable for security)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Create a directory to store generated PDFs
os.makedirs("documents", exist_ok=True)

# Function to generate legal text using OpenAI
def generate_legal_text(doc_type, user_data):
    prompt = f"Generate a {doc_type} agreement between {user_data['name']} and {user_data['party']}. Ensure it follows Indian legal standards."
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are a legal assistant trained in Indian law."},
                  {"role": "user", "content": prompt}]
    )
    return response["choices"][0]["message"]["content"]

# Function to generate legal document PDF
def generate_legal_document(doc_type, user_data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Title
    pdf.cell(200, 10, txt=f"{doc_type} Agreement", ln=True, align='C')
    pdf.ln(10)

    # Generate legal text using OpenAI
    legal_text = generate_legal_text(doc_type, user_data)

    # Content
    pdf.multi_cell(0, 10, txt=legal_text)

    # Save PDF file
    pdf_filename = f"documents/{doc_type}_agreement_{user_data['name']}.pdf"
    pdf.output(pdf_filename)
    return pdf_filename

# API Endpoint: Generate Document
@app.route('/generate-document', methods=['POST'])
def generate_document():
    data = request.json
    doc_type = data.get("doc_type", "General")
    user_data = data.get("user_data", {"name": "User", "party": "Other Party"})

    pdf_filename = generate_legal_document(doc_type, user_data)

    return jsonify({"message": "Document Generated", "document_url": f"http://127.0.0.1:5000/download-document/{os.path.basename(pdf_filename)}"})

# API Endpoint: Download Document
@app.route('/download-document/<filename>', methods=['GET'])
def download_document(filename):
    file_path = f"documents/{filename}"
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({"error": "File not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
