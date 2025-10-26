from flask import Flask, render_template, request, jsonify
import pandas as pd
import json
import os
from models import call_all_models, MODELS


app = Flask(__name__)
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