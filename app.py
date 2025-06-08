import os
import json
from flask import Flask, render_template, request

# --- Flask setup ---
app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)

# --- Path to your data ---
CHUNKS_PATH = os.path.join("data", "chunks.json")

chunks = []
documents = []
refine_options = []
error_message = ""

# --- Load chunks safely ---
try:
    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        chunks = json.load(f)
        documents = sorted(set(chunk.get("document", "Unknown") for chunk in chunks))
        refine_options = sorted(set(chunk.get("section", "Uncategorised") for chunk in chunks if chunk.get("section")))
except FileNotFoundError:
    error_message = f"ERROR: Could not find {CHUNKS_PATH}"
except json.JSONDecodeError:
    error_message = f"ERROR: {CHUNKS_PATH} is not valid JSON"
except Exception as e:
    error_message = f"UNEXPECTED ERROR: {str(e)}"

# --- Main route ---
@app.route("/", methods=["GET", "POST"])
def index():
    question = ""
    results = []
    selected_doc = None
    selected_section = None

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
        selected_section=selected_section,
        error=error_message
    )

# --- Autocomplete endpoint ---
@app.route("/autocomplete", methods=["GET"])
def autocomplete():
    query = request.args.get("query", "").strip().lower()
    filename = request.args.get("filename")

    suggestions = set()
    for chunk in chunks:
        if filename and filename != "All Documents" and chunk.get("document") != filename:
            continue
        content = chunk.get("content", "").lower()
        if query in content:
            suggestions.add(chunk.get("section", "Uncategorised"))

    return {"suggestions": sorted(suggestions)}

# --- Ensure correct port on Render ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
