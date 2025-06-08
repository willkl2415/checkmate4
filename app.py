import os
import json
from flask import Flask, render_template, request, jsonify

app = Flask(__name__, template_folder="templates", static_folder="static")

CHUNKS_PATH = os.path.join("data", "chunks.json")

# --- Load all chunks
chunks = []
try:
    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        chunks = json.load(f)
except Exception as e:
    print(f"Failed to load chunks.json: {e}")

@app.route("/", methods=["GET", "POST"])
def index():
    question = ""
    results = []
    selected_doc = None
    selected_section = None

    documents = sorted(set(chunk.get("document", "Unknown") for chunk in chunks))
    refine_options = sorted(set(chunk.get("section", "Uncategorised") for chunk in chunks if chunk.get("section")))

    if request.method == "POST":
        question = request.form.get("question", "").strip().lower()
        selected_doc = request.form.get("document")
        selected_section = request.form.get("refine")

        for chunk in chunks:
            if question in chunk.get("content", "").lower():
                if selected_doc and selected_doc != "All Documents" and chunk.get("document") != selected_doc:
                    continue
                if selected_section and selected_section != "All Sections" and chunk.get("section") != selected_section:
                    continue
                results.append(chunk)

    return render_template(
        "index.html",
        question=question,
        results=results,
        documents=documents,
        refine_options=refine_options,
        selected_doc=selected_doc,
        selected_section=selected_section
    )

@app.route("/autocomplete")
def autocomplete():
    query = request.args.get("query", "").lower()
    filename = request.args.get("filename", "")

    matches = set()
    for chunk in chunks:
        if filename != "All Documents" and chunk.get("document") != filename:
            continue
        content = chunk.get("content", "")
        words = [word.strip(".,:;()[]") for word in content.lower().split()]
        matches.update(word for word in words if word.startswith(query) and len(word) > 3)

    return jsonify(sorted(list(matches))[:15])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
