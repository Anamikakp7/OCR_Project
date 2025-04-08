from flask import Flask, request, jsonify, render_template
import easyocr
import fitz  # PyMuPDF for PDF text extraction
import os
import paho.mqtt.client as mqtt

app = Flask(__name__)

# MQTT Configuration
#MQTT_BROKER = "mqtt.eclipseprojects.io"  # Change to your broker IP/URL
MQTT_BROKER = "broker.rithask.me" 
MQTT_PORT = 1883
MQTT_TOPIC = "haptomapping"
#MQTT_TOPIC = "hardware/output"

client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Initialize EasyOCR reader for images
reader = easyocr.Reader(['en'])

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    text_input = request.form.get('textInput', '')
    file = request.files.get('imageInput')

    extracted_text = ""

    # Case 1: Text is provided in the textbox
    if text_input:
        extracted_text = text_input

    # Case 2: File (Image or PDF) is uploaded
    elif file:
        file_path = os.path.join('uploads', file.filename)
        os.makedirs('uploads', exist_ok=True)
        file.save(file_path)

        file_ext = file.filename.split('.')[-1].lower()
        try:
            if file_ext == 'pdf':
                # Extract text directly from PDF using PyMuPDF
                pdf_document = fitz.open(file_path)
                for page in pdf_document:
                    extracted_text += page.get_text() + "\n"
                pdf_document.close()
            else:
                # Process as an image using EasyOCR
                results = reader.readtext(file_path, detail=0)
                extracted_text = " ".join(results)

            os.remove(file_path)  # Cleanup uploaded file

        except Exception as e:
            return jsonify({"text": f"Error processing the file: {str(e)}"})

    else:
        return jsonify({"text": "No input provided"})

    # Publish extracted text to MQTT
    client.publish(MQTT_TOPIC, extracted_text)

    return jsonify({"text": extracted_text})

if __name__ == '__main__':
    app.run(debug=True)
