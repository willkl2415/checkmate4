import os
import json
from flask import Flask, render_template, request, jsonify

app = Flask(__name__, template_folder="templates", static_folder="static")

CHUNKS_PATH = os.path.join("data", "chunks.json")

chunks = []
documents = []
refine_map = {}
error_message = ""

# Load chunks and create document-to-section map
try:
    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        chunks = json.load(f)
        documents = sorted(set(chunk.get("document", "Unknown") for chunk in chunks))

        for chunk in chunks:
            doc = chunk.get("document", "Unknown")
            sec = chunk.get("section", "Uncategorised")
            if doc not in refine_map:
                refine_map[doc] = set()
            if sec:
                refine_map[doc].add(sec)
except Exception as e:
    error_message = str(e)

@app.route("/", methods=["GET", "POST"])
def index():
    question = ""
    results = []
    selected_doc = "All Documents"
    selected_section = "All Sections"

    if request.method == "POST":
        question = request.form.get("question", "").strip().lower()
        selected_doc = request.form.get("document", "All Documents")
        selected_section = request.form.get("refine", "All Sections")

        for chunk in chunks:
            if question in chunk.get("content", "").lower():
                if selected_doc != "All Documents" and chunk.get("document") != selected_doc:
                    continue
                if selected_section != "All Sections" and chunk.get("section") != selected_section:
                    continue
                results.append(chunk)

    refine_options = sorted(refine_map.get(selected_doc, [])) if selected_doc != "All Documents" else []

    return render_template(
        "index.html",
        question=question,
        results=results,
        documents=documents,
        refine_options=refine_options,
        selected_doc=selected_doc,
        selected_section=selected_section,
        error=error_message
    )

@app.route("/get_sections")
def get_sections():
    selected_doc = request.args.get("document", "All Documents")
    options = sorted(refine_map.get(selected_doc, [])) if selected_doc in refine_map else []
    return jsonify(options)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
