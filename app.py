import os
import json
from flask import Flask, render_template, request

app = Flask(__name__, template_folder="templates", static_folder="static")

CHUNKS_PATH = os.path.join("data", "chunks.json")

chunks = []
documents = []
sections_by_document = {}
error_message = ""

# Load data
try:
    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        chunks = json.load(f)
        documents = sorted(set(chunk.get("document", "Unknown") for chunk in chunks))
        for chunk in chunks:
            doc = chunk.get("document", "Unknown")
            sec = chunk.get("section", "Uncategorised")
            if doc not in sections_by_document:
                sections_by_document[doc] = set()
            sections_by_document[doc].add(sec)
except FileNotFoundError:
    error_message = f"ERROR: Could not find {CHUNKS_PATH}"
except json.JSONDecodeError:
    error_message = f"ERROR: {CHUNKS_PATH} is not valid JSON"
except Exception as e:
    error_message = f"UNEXPECTED ERROR: {str(e)}"

@app.route("/", methods=["GET", "POST"])
def index():
    question = ""
    results = []
    selected_doc = "All Documents"
    selected_section = "All Sections"
    refine_options = sorted(set(sec for secs in sections_by_document.values() for sec in secs))

    if request.method == "POST":
        question = request.form.get("question", "").strip().lower()
        selected_doc = request.form.get("document", "All Documents")
        selected_section = request.form.get("refine", "All Sections")

        # Refine options update
        if selected_doc != "All Documents":
            refine_options = sorted(sections_by_document.get(selected_doc, []))
        else:
            refine_options = sorted(set(sec for secs in sections_by_document.values() for sec in secs))

        # Search logic
        for chunk in chunks:
            if question in chunk.get("content", "").lower():
                if selected_doc != "All Documents" and chunk.get("document") != selected_doc:
                    continue
                if selected_section != "All Sections" and chunk.get("section") != selected_section:
                    continue
                results.append(chunk)

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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
