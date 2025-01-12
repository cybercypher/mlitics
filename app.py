from flask import Flask, request, jsonify
import requests
from concurrent.futures import ThreadPoolExecutor
import logging
from marshmallow import Schema, fields, ValidationError

# Flask app initialization
app = Flask(__name__)

# Thread pool for concurrent requests
executor = ThreadPoolExecutor(max_workers=5)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Utility function to get headers
def get_headers(api_key):
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

# Utility function to extract API key from request
def get_api_key():
    return request.args.get("api_key") or request.headers.get("Authorization")

# Generic function to make API requests
def make_request(method, endpoint, api_key, params=None, data=None):
    url = f"https://app.mentionlytics.com/api/{endpoint}"
    params = params or {}
    params['token'] = api_key

    logger.info(f"Making {method} request to {url} with params: {params} and data: {data}")

    try:
        response = requests.request(
            method=method, url=url, headers=get_headers(api_key), params=params, json=data
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        return {"error": str(e)}, 500

    if response.status_code != 200:
        logger.error(f"Request error: {response.status_code} - {response.text}")
        return {"error": response.json().get("message", "Unknown error")}, response.status_code

    logger.info(f"Response: {response.status_code}, {response.text}")
    return response.json()

# Input validation schema for creating an alert
class AlertSchema(Schema):
    project_id = fields.Str(required=True)
    name = fields.Str(required=True)
    keywords = fields.List(fields.Str(), required=True)

# Route to get mentions by keyword
@app.route("/mentions", methods=["GET"])
def get_mentions():
    api_key = get_api_key()
    if not api_key:
        return jsonify({"error": "API key is required"}), 401

    keyword = request.args.get("keyword")
    project_id = request.args.get("project_id")

    if not keyword or not project_id:
        return jsonify({"error": "keyword and project_id are required"}), 400

    future = executor.submit(
        make_request, "GET", "mentions", api_key, {"keyword": keyword, "project_id": project_id}
    )
    result = future.result()
    return jsonify(result)

# Route to create a new alert
@app.route("/alerts", methods=["POST"])
def create_alert():
    api_key = get_api_key()
    if not api_key:
        return jsonify({"error": "API key is required"}), 401

    data = request.json
    try:
        AlertSchema().load(data)
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    future = executor.submit(
        make_request,
        "POST",
        "alerts",
        api_key,
        None,
        {"project_id": data["project_id"], "name": data["name"], "keywords": data["keywords"]},
    )
    result = future.result()
    return jsonify(result)

# Route to get all alerts for a project
@app.route("/alerts", methods=["GET"])
def get_alerts():
    api_key = get_api_key()
    if not api_key:
        return jsonify({"error": "API key is required"}), 401

    project_id = request.args.get("project_id")
    if not project_id:
        return jsonify({"error": "project_id is required"}), 400

    future = executor.submit(make_request, "GET", "alerts", api_key, {"project_id": project_id})
    result = future.result()
    return jsonify(result)

# Route to get all projects
@app.route("/projects", methods=["GET"])
def get_projects():
    api_key = get_api_key()
    if not api_key:
        return jsonify({"error": "API key is required"}), 401

    future = executor.submit(make_request, "GET", "projects", api_key)
    result = future.result()
    return jsonify(result)

# Route to get metrics for a project
@app.route("/projects/<project_id>/metrics", methods=["GET"])
def get_project_metrics(project_id):
    api_key = get_api_key()
    if not api_key:
        return jsonify({"error": "API key is required"}), 401

    future = executor.submit(make_request, "GET", f"projects/{project_id}/metrics", api_key)
    result = future.result()
    return jsonify(result)

# Run the Flask app with multi-threading enabled
if __name__ == "__main__":
    app.run(debug=True, threaded=True)