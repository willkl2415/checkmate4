from flask import Flask, render_template, request
import json
import os

app = Flask(__name__)

# Correct path to the chunks file
CHUNKS_PATH = os.path.join("data", "chunks.json")
with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
    chunks = json.load(f)

# Build dropdown values
documents = sorted(set(chunk.get("document", "Unknown") for chunk in chunks))
refine_options = sorted(set(chunk.get("section", "Uncategorised") for chunk in chunks if chunk.get("section")))

@app.route("/", methods=["GET", "POST"])
def index():
    question = ""
    results = []

    if request.method == "POST":
        question = request.form.get("question", "").strip().lower()
        selected_doc = request.form.get("document")
        selected_section = request.form.get("refine")

        for chunk in chunks:
            if question in chunk.get("content", "").lower():
                if selected_doc and chunk.get("document") != selected_doc:
                    continue
                if selected_section and chunk.get("section") != selected_section:
                    continue
                results.append(chunk)

    return render_template(
        "index.html",
        question=question,
        results=results,
        documents=documents,
        refine_options=refine_options
    )

if __name__ == "__main__":
    app.run(debug=True)
