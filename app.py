from flask import Flask, request, jsonify
import requests
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

# Replace with your Mentionlytics API Key
API_KEY = "your_api_key_here"
BASE_URL = "https://api.mentionlytics.com/v1"

# Thread pool for making concurrent requests
executor = ThreadPoolExecutor(max_workers=5)

def get_headers():
    """
    Returns the headers required for Mentionlytics API requests.
    """
    return {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

def make_request(method, endpoint, params=None, data=None):
    """
    Generic function to make requests to the Mentionlytics API.
    """
    url = f"{BASE_URL}/{endpoint}"
    response = requests.request(
        method=method,
        url=url,
        headers=get_headers(),
        params=params,
        json=data
    )

    if response.status_code != 200:
        return {"error": response.text}, response.status_code

    return response.json()

@app.route('/mentions', methods=['GET'])
def get_mentions():
    """
    Endpoint to fetch mentions by keyword (multi-threaded).
    """
    keyword = request.args.get('keyword')
    page = request.args.get('page', 1)

    if not keyword:
        return jsonify({"error": "Keyword is required"}), 400

    # Use ThreadPoolExecutor to make the request asynchronously
    future = executor.submit(make_request, "GET", "mentions", {"keyword": keyword, "page": page})
    result = future.result()

    return jsonify(result)

@app.route('/alerts', methods=['POST'])
def create_alert():
    """
    Endpoint to create a new alert.
    """
    data = request.json
    name = data.get("name")
    keywords = data.get("keywords")

    if not name or not keywords:
        return jsonify({"error": "Name and keywords are required"}), 400

    # Use ThreadPoolExecutor to make the request asynchronously
    future = executor.submit(make_request, "POST", "alerts", None, {"name": name, "keywords": keywords})
    result = future.result()

    return jsonify(result)

@app.route('/alerts', methods=['GET'])
def get_alerts():
    """
    Endpoint to fetch all alerts.
    """
    # Use ThreadPoolExecutor to make the request asynchronously
    future = executor.submit(make_request, "GET", "alerts")
    result = future.result()

    return jsonify(result)

if __name__ == "__main__":
    # Enable multi-threading by setting threaded=True
    app.run(debug=True, threaded=True)

