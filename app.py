from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from transformers import pipeline
import re

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

def extract_keywords(query):
    """Extracts the most important words from a query"""
    # Split query into words & remove common stop words
    stop_words = {"the", "is", "for", "in", "and", "of", "to", "with", "a", "what","an"}  
    words = re.findall(r'\b\w+\b', query.lower())  # Get words only
    keywords = [word for word in words if word not in stop_words]
    
    return keywords
@app.route("/")
def home():
    return render_template("index.html")  # Serve HTML file

@app.route("/query", methods=["POST"])
def query():
    data = request.get_json()
    user_query = data.get("query", "").strip()

    if not user_query:
        return jsonify({"error": "No query provided"}), 400

    keywords = extract_keywords(user_query)
    keyword_query = " ".join(keywords)  # Reform the query with keywords only

    # Perform similarity search on original and refined query
    results1 = db.similarity_search(user_query, k=3)  # Original query
    results2 = db.similarity_search(keyword_query, k=3)  # Keyword-focused query

    # Combine & deduplicate results
    seen = set()
    final_results = []
    for res in results1 + results2:
        if res.page_content not in seen:
            seen.add(res.page_content)
            final_results.append(res)

    # Format response
    response = {
        "results": [
            {
                "content": res.page_content,
                "source": res.metadata.get("source", "Unknown"),
                "pdf_link": res.metadata.get("url", "#")
            }
            for res in final_results
        ]
    }
    return jsonify(response)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
