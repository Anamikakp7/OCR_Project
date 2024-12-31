from flask import Flask, request, jsonify, render_template
import easyocr
import fitz  # PyMuPDF for PDF text extraction
import os

app = Flask(__name__)

# Initialize EasyOCR reader for images
reader = easyocr.Reader(['en'])

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    text_input = request.form.get('textInput', '')
    file = request.files.get('imageInput')

    # Case 1: Text is provided in the textbox
    if text_input:
        return jsonify({"text": text_input})

    # Case 2: File (Image or PDF) is uploaded
    if file:
        file_path = os.path.join('uploads', file.filename)
        os.makedirs('uploads', exist_ok=True)
        file.save(file_path)

        file_ext = file.filename.split('.')[-1].lower()
        extracted_text = ""

        try:
            if file_ext == 'pdf':
                # Extract text directly from PDF using PyMuPDF
                pdf_document = fitz.open(file_path)
                for page_number in range(len(pdf_document)):
                    page = pdf_document[page_number]
                    extracted_text += page.get_text() + "\n"
                pdf_document.close()
            else:
                # Process as an image using EasyOCR
                results = reader.readtext(file_path, detail=0)
                extracted_text = " ".join(results)

            os.remove(file_path)  # Cleanup uploaded file
            return jsonify({"text": extracted_text.strip()})

        except Exception as e:
            return jsonify({"text": f"Error processing the file: {str(e)}"})

    return jsonify({"text": "No input provided"})

if __name__ == '__main__':
    app.run(debug=True)

