from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)  # Enable CORS if needed

@app.route("/")
def home():
    return render_template("index.html")  # Serve HTML file

@app.route("/query", methods=["POST"])
def query():
    data = request.get_json()
    user_query = data.get("query", "")

    if not user_query:
        return jsonify({"error": "No query provided"}), 400

    results = db.similarity_search(user_query, k=2)

    response = {"results": [{"content": res.page_content, "source": res.metadata.get("source", "Unknown")} for res in results]}
    return jsonify(response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
