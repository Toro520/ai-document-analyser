from flask import Flask, request, jsonify, render_template
import pdfplumber
from openai import OpenAI

app = Flask(__name__)
import os
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


@app.route("/")
def index():
    return render_template("index.html")
@app.route("/")
def hello():
    return "I am ready to start it"


@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "你是一个文档分析助手，用中文回答。"},
            {"role": "user", "content": f"请总结这份文档的主要内容，100字以内：\n\n{text[:3000]}"}
        ]
    )

    summary = response.choices[0].message.content

    return app.response_class(
        response=__import__('json').dumps({
            "filename": file.filename,
            "word_count": len(text.split()),
            "summary": summary
        }, ensure_ascii=False),
        mimetype='application/json'
    )


if __name__ == "__main__":
    app.run(debug=True)