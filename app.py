from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_text', methods=['POST'])
def generate_text():
    try:
        # Extracting input from the form
        prompt = request.form['prompt']

        invoke_url = "https://api.nvcf.nvidia.com/v2/nvcf/pexec/functions/2ae529dc-f728-4a46-9b8d-2697213666d8"
        fetch_url_format = "https://api.nvcf.nvidia.com/v2/nvcf/pexec/status/"

        headers = {
            "Authorization": "Bearer ***paste yout nvidia api here*** ",
            "Accept": "application/json",
        }

        payload = {
            "messages": [{"content": prompt, "role": "user"}],
            "temperature": 0.2,
            "top_p": 0.7,
            "max_tokens": 1024,
            "seed": 42,
            "stream": False,
        }

        # Re-use connections
        session = requests.Session()

        # Sending the initial API request
        response = session.post(invoke_url, headers=headers, json=payload)
        response.raise_for_status()  # Check for HTTP errors

        while response.status_code == 202:
            request_id = response.headers.get("NVCF-REQID")
            if not request_id:
                raise ValueError("Missing NVCF-REQID in response headers")

            fetch_url = fetch_url_format + request_id
            response = session.get(fetch_url, headers=headers)
            response.raise_for_status()  # Check for HTTP errors

        response_body = response.json()
        generated_text = response_body['choices'][0]['message']['content']

    except Exception as e:
        generated_text = f"Error: {str(e)}"

    finally:
        session.close()

    return jsonify({'generated_text': generated_text})

if __name__ == '__main__':
    app.run(debug=True)
