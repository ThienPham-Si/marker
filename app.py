from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
from marker.scripts.convert_single import convert_single_cli
import tempfile
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configure upload settings
UPLOAD_FOLDER = tempfile.gettempdir()  # Use system temp directory
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'docx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/convert', methods=['POST'])
def convert_file():
    logger.debug("Received conversion request")
    
    if 'file' not in request.files:
        logger.error("No file part in request")
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        logger.error("No selected file")
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        try:
            logger.info(f"Processing file: {file.filename}")
            # Save uploaded file
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Process the file
            output_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'output')
            os.makedirs(output_dir, exist_ok=True)
            
            convert_single_cli([
                filepath,
                '--output_format', 'markdown',
                '--output_dir', output_dir
            ])
            
            return jsonify({
                'success': True,
                'filename': file.filename
            })
            
        except Exception as e:
            logger.error(f"Error processing file: {str(e)}", exc_info=True)
            return jsonify({'error': str(e)}), 500
            
    logger.error(f"Invalid file type: {file.filename}")
    return jsonify({'error': 'File type not allowed'}), 400

# Add a test endpoint
@app.route('/test', methods=['GET'])
def test():
    return jsonify({'message': 'Server is running'}), 200

if __name__ == '__main__':
    app.run(debug=True, port=8000, host='0.0.0.0')
