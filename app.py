from flask import Flask, render_template, request, jsonify
import pandas as pd
import json
import os
from models import call_all_models, MODELS


app = Flask(__name__)
@app.route("/")
def index():
    return render_template("index.html", models=list(MODELS.keys()))
@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    prompt = data.get("prompt")
    categorie = data.get("categorie")
    
    resultats = call_all_models(prompt)
    
    return jsonify({
        "prompt": prompt,
        "categorie": categorie,
        "resultats": resultats
    })
@app.route("/upload", methods=["POST"])
def upload():
    fichier = request.files["file"]
    phrases = fichier.read().decode("utf-8").splitlines()
    phrases = [p.strip() for p in phrases if p.strip()]
    return jsonify({"phrases": phrases})
@app.route("/export/csv", methods=["POST"])
def export_csv():
    data = request.json
    df = pd.DataFrame(data)
    path = "exports/resultats.csv"
    df.to_csv(path, index=False, encoding="utf-8")
    return jsonify({"message": "Export CSV ok", "path": path})  
@app.route("/export/latex", methods=["POST"])
def export_latex():
    data = request.json
    df = pd.DataFrame(data)
    latex = df.to_latex(index=False, escape=True)
    path = "exports/resultats.tex"
    with open(path, "w", encoding="utf-8") as f:
        f.write(latex)
    return jsonify({"message": "Export LaTeX ok", "path": path})
@app.post("/eval")
def eval_route(data):
    data = request.get_json()
    prompt = data["prompt"]

    resultats = {
        name: call_eval_model(prompt, name)
        for name in MODELS
    }
    return {"resultats": resultats}
if __name__ == "__main__":
    app.run(debug=True)
    
