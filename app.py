from flask import Flask, request, jsonify
import requests
from concurrent.futures import ThreadPoolExecutor

# Flask app initialization
app = Flask(__name__)

# Thread pool for concurrent requests
executor = ThreadPoolExecutor(max_workers=5)

# Utility function to get headers
def get_headers(api_key):
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

# Generic function to make API requests
def make_request(method, endpoint, api_key, params=None, data=None):
    url = f"https://api.mentionlytics.com/v1/{endpoint}"
    response = requests.request(
        method=method, url=url, headers=get_headers(api_key), params=params, json=data
    )

    if response.status_code != 200:
        return {"error": response.text}, response.status_code
    return response.json()

# Route to get mentions by keyword
@app.route("/mentions", methods=["GET"])
def get_mentions():
    api_key = request.args.get("api_key") or request.headers.get("Authorization")
    keyword = request.args.get("keyword")
    project_id = request.args.get("project_id")

    if not api_key:
        return jsonify({"error": "API key is required"}), 400
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
    api_key = request.args.get("api_key") or request.headers.get("Authorization")
    data = request.json

    if not api_key:
        return jsonify({"error": "API key is required"}), 400
    if not data.get("project_id") or not data.get("name") or not data.get("keywords"):
        return jsonify({"error": "project_id, name, and keywords are required"}), 400

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
    api_key = request.args.get("api_key") or request.headers.get("Authorization")
    project_id = request.args.get("project_id")

    if not api_key:
        return jsonify({"error": "API key is required"}), 400
    if not project_id:
        return jsonify({"error": "project_id is required"}), 400

    future = executor.submit(make_request, "GET", "alerts", api_key, {"project_id": project_id})
    result = future.result()
    return jsonify(result)

# Route to get all projects
@app.route("/projects", methods=["GET"])
def get_projects():
    api_key = request.args.get("api_key") or request.headers.get("Authorization")

    if not api_key:
        return jsonify({"error": "API key is required"}), 400

    future = executor.submit(make_request, "GET", "projects", api_key)
    result = future.result()
    return jsonify(result)

# Route to get metrics for a project
@app.route("/projects/<project_id>/metrics", methods=["GET"])
def get_project_metrics(project_id):
    api_key = request.args.get("api_key") or request.headers.get("Authorization")

    if not api_key:
        return jsonify({"error": "API key is required"}), 400

    future = executor.submit(make_request, "GET", f"projects/{project_id}/metrics", api_key)
    result = future.result()
    return jsonify(result)

# Run the Flask app with multi-threading enabled
if __name__ == "__main__":
    app.run(debug=True, threaded=True)

