from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings

app = Flask(__name__)
CORS(app)  # Allows frontend to access API

# Load FAISS index
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)

@app.route("/query", methods=["POST"])
def query():
    data = request.json
    user_query = data.get("query", "")
    if not user_query:
        return jsonify({"error": "No query provided"}), 400

    results = db.similarity_search(user_query, k=2)
    response = [{"content": res.page_content} for res in results]
    
    return jsonify(response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
