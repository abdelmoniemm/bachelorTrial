from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import json
from pathlib import Path
import sys
import os

# --- Flask App Setup ---
app = Flask(__name__)
# CORS is needed to allow the HTML file to talk to this server
CORS(app)

# --- Configuration ---
# This script assumes it's in the same directory as the 'bachelor' folder
SCRIPT_PATH = Path(__file__).parent
LOCAL_PATH = SCRIPT_PATH / "bachelor"
GRAPHDB_URL = "http://localhost:7200/repositories/AbdelBachelor2025"

# --- Helper Functions ---
def log_and_run(command, step_name):
    """Runs a command and logs its output, raising an error on failure."""
    print(f"--- Running: {step_name} ---")
    process = subprocess.run(
        command, 
        capture_output=True, 
        text=True, 
        encoding='utf-8', 
        check=True # This will raise CalledProcessError on non-zero exit codes
    )
    if process.stdout:
        print(f"[LOG] {process.stdout.strip()}")
    if process.stderr:
        print(f"[WARNING] {process.stderr.strip()}")
    return f"{step_name} completed successfully."

# --- API Endpoint ---
@app.route('/run-pipeline', methods=['POST'])
def run_pipeline():
    """
    This is the main API endpoint. It receives the raw JSON data,
    runs the entire pipeline, and returns the result.
    """
    # 1. --- Validate and Save Uploaded File ---
    if 'dataFile' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['dataFile']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if file:
        # Save the uploaded file temporarily
        raw_data_path = LOCAL_PATH / "temp_raw_data.json"
        file.save(raw_data_path)
        print(f"Saved temporary raw data to {raw_data_path}")

        try:
            # 2. --- Transform JSON and Overwrite data.json ---
            print("--- Transforming and Overwriting data.json ---")
            target_path = LOCAL_PATH / "data.json"
            original_content = raw_data_path.read_text(encoding='utf-8')
            start_index = original_content.find('[')
            end_index = original_content.rfind(']')
            if start_index == -1 or end_index == -1:
                raise ValueError("Could not find a valid JSON array '[]' in the input file.")
            
            json_array_str = original_content[start_index : end_index + 1]
            transformed_data = {"rules": json.loads(json_array_str)}
            target_path.write_text(json.dumps(transformed_data, indent=2), encoding='utf-8')
            print(f"Successfully transformed and overwrote '{target_path}'")

            # 3. --- Run Docker Commands ---
            print("--- Running Docker mapping process ---")
            # Docker command 1: YARRRML to RML
            yarrrml_to_rml_cmd = [
                "docker", "run", "--rm",
                "-v", f"{LOCAL_PATH}:/data",
                "rmlio/yarrrml-parser:1.10.0", "-i", "/data/rules.yml", "-o", "/data/rules.rml.ttl"
            ]
            log_and_run(yarrrml_to_rml_cmd, "YARRRML-to-RML Conversion")
            
            # Docker command 2: RML to RDF
            rml_to_rdf_cmd = [
                "docker", "run", "--rm",
                "-v", f"{LOCAL_PATH}:/data",
                "rmlio/rmlmapper-java:v7.3.3", "-m", "/data/rules.rml.ttl", "-o", "/data/output.ttl"
            ]
            log_and_run(rml_to_rdf_cmd, "RML-to-RDF Conversion")
            
            # 4. --- Auto-Import to GraphDB ---
            print("--- Importing to GraphDB ---")
            output_ttl_path = LOCAL_PATH / "output.ttl"
            if not output_ttl_path.exists():
                raise FileNotFoundError("'output.ttl' was not created by the mapping process.")
            
            with open(output_ttl_path, 'rb') as f:
                headers = {'Content-Type': 'application/x-turtle'}
                response = requests.post(f"{GRAPHDB_URL}/statements", data=f, headers=headers)
                response.raise_for_status() # Raise error for bad responses
            
            print("--- Pipeline finished successfully! ---")
            # 5. --- Return Success Response ---
            return jsonify({"message": "Pipeline completed successfully! Data has been imported to GraphDB."})

        except Exception as e:
            print(f"[ERROR] Pipeline failed: {e}")
            # Return a detailed error message to the frontend
            return jsonify({"error": f"Pipeline failed: {str(e)}"}), 500
        finally:
            # Clean up the temporary file
            if raw_data_path.exists():
                os.remove(raw_data_path)

if __name__ == '__main__':
    # Ensure the 'bachelor' directory exists
    if not LOCAL_PATH.exists():
        LOCAL_PATH.mkdir()
        print(f"Created directory: {LOCAL_PATH}")
    # Run the Flask app
    app.run(debug=True, port=5001)

