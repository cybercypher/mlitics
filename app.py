from flask import Flask, request, jsonify
import requests
import logging
import os

# Flask app initialization
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Utility function to extract token from the request
def get_token():
    token = request.args.get("api_key")
    if not token:
        secret_path = "/run/secrets/mentionlytics_token"
        if os.path.exists(secret_path):
            with open(secret_path, "r") as secret_file:
                token = secret_file.read().strip()
    return token

# Generic function to make API requests
def make_request(method, endpoint, token, params=None, data=None):
    url = f"https://app.mentionlytics.com/api/{endpoint}"
    params = params or {}
    params['token'] = token

    # Ensure data is forwarded as None if not provided
    data = data if data else None

    logger.info(f"Making {method} request to {url} with params: {params} and data: {data}")

    try:
        response = requests.request(
            method=method,
            url=url,
            headers={"Content-Type": "application/json"},  # Only forward Content-Type
            params=params,
            json=data,
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        return {"error": str(e)}, 500

    if response.status_code != 200:
        logger.error(f"Request error: {response.status_code} - {response.text}")
        return {"error": response.json().get("message", "Unknown error")}, response.status_code

    return response.json()

# Catch-all route to forward all requests
@app.route("/<path:endpoint>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def proxy_request(endpoint):
    token = get_token()
    if not token:
        return jsonify({"error": "API key is required"}), 401

    params = {key: value for key, value in request.args.items() if key != "api_key"}
    data = request.get_json() if request.is_json else None

    # Replace 'api_key' with 'token' in params
    if "api_key" in params:
        params["token"] = params.pop("api_key")

    result = make_request(request.method, endpoint, token, params, data)
    return jsonify(result)

# Run the Flask app with multi-threading enabled
if __name__ == "__main__":
    app.run(debug=True, threaded=True)
