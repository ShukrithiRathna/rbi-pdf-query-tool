from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)  # Enable CORS if needed

# Load embeddings model
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Load PDF links into a dictionary {filename: url}
def load_pdf_links(file_path="pdf_links.txt"):
    pdf_map = {}
    with open(file_path, "r") as f:
        for line in f:
            url = line.strip()
            filename = url.split("/")[-1]  # Extract filename from URL
            pdf_map[filename] = url
    return pdf_map

# Load at startup
pdf_links = load_pdf_links()

# Load FAISS database
FAISS_INDEX_PATH = "faiss_index_meta"  # Adjust this path if needed
db = FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)

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

    response = {
        "results": [
            {
                "content": res.page_content,
                "source": res.metadata.get("source", "Unknown"),
                "url": pdf_links.get(res.metadata.get("source", ""), "URL Not Found")  # Match with dictionary
            }
            for res in results
        ]
    }
    return jsonify(response)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
