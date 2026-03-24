let tousResultats = [];

async function chargerFichier() {
    const fichier = document.getElementById("fichier").files[0];
    if (!fichier) return alert("Sélectionne un fichier .txt !");

    const formData = new FormData();
    formData.append("file", fichier);

    const response = await fetch("/upload", {
        method: "POST",
        body: formData
    });

    const data = await response.json();

    const liste = document.getElementById("liste-phrases");
    liste.innerHTML = "";

    data.phrases.forEach(phrase => {
        const div = document.createElement("div");
        div.className = "phrase-item";
        div.textContent = phrase;
        liste.appendChild(div);
    });

    await analyserListe(data.phrases);
}

async function analyserListe(phrases) {
    const categorie = document.getElementById("categorie").value;

    tousResultats = [];

    for (const phrase of phrases) {

        const prompt_final =
            `Y a-t-il une présupposition dans cette phrase : "${phrase}" ? Si oui, laquelle ?`;

        const res = await fetch("/analyze", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                prompt: prompt_final,
                phrase,
                categorie
            })
        });

        const data = await res.json();

        const resultats = data.resultats || {};


        const clean = {
            id: `EXP${String(tousResultats.length + 1).padStart(2, "0")}`,
            phrase: phrase,

            ChatGPT: getValue(resultats, "ChatGPT"),
            Claude: getValue(resultats, "Claude"),
            Deepseek: getValue(resultats, "Deepseek"),
            "Meta AI": getValue(resultats, "Meta"),
            Mistral: getValue(resultats, "Mistral"),

            human_eval: {
                ChatGPT: null,
                Claude: null,
                Deepseek: null,
                "Meta AI": null,
                Mistral: null
            }
        };

        tousResultats.push(clean);
    }

    renderTable(tousResultats);
}

async function analyser() {
    const texte = document.getElementById("prompt").value.trim();
    const categorie = document.getElementById("categorie").value;

    if (!texte) return alert("Entre au moins une phrase !");

    const phrases = texte
        .split("\n")
        .map(p => p.trim())
        .filter(Boolean);

    const btn = document.querySelector("button[onclick='analyser()']");
    btn.textContent = "Analyse...";
    btn.disabled = true;

    await analyserListe(phrases);

    btn.textContent = "Analyser les modèles";
    btn.disabled = false;
}

/* =========================
   TABLE RENDER
========================= */
function renderTable(data) {
    const tbody = document.getElementById("tbody-resultats");
    tbody.innerHTML = "";

    data.forEach(item => {

        const tr = document.createElement("tr");

        tr.innerHTML = `
            <td>${item.id}</td>
            <td>${escapeHTML(item.phrase)}</td>
            <td>${escapeHTML(item.ChatGPT)}</td>
            <td>${escapeHTML(item.Claude)}</td>
            <td>${escapeHTML(item.Deepseek)}</td>
            <td>${escapeHTML(item["Meta AI"])}</td>
            <td>${escapeHTML(item.Mistral)}</td>

            <!-- HUMAN EVAL -->
            <td>
                ${renderEvalSelector(item.id)}
            </td>
        `;

        tbody.appendChild(tr);
    });

    document.getElementById("section-resultats").classList.remove("hidden");
}

/* =========================
   🧠 EVAL UI
========================= */
function renderEvalSelector(id) {
    return `
        <select onchange="saveEval('${id}', this.value)">
            <option value="">--</option>
            <option value="VP">VP</option>
            <option value="FP">FP</option>
            <option value="FN">FN</option>
            <option value="VN">VN</option>
        </select>
    `;
}

function saveEval(id, value) {
    const item = tousResultats.find(x => x.id === id);
    if (!item) return;

    item.human_eval.global = value;
}

/* =========================
   EXTRACTION ROBUSTE MODELES
========================= */
function getValue(obj, key) {
    if (!obj) return "";

    if (obj[key]) return obj[key];

    const found = Object.entries(obj).find(([k]) =>
        k.toLowerCase().includes(key.toLowerCase())
    );

    return found ? found[1] : "";
}

/* =========================
   EVALUATION MODE (DEBUG)
========================= */
async function evaluer() {

    const texte = document.getElementById("prompt").value.trim();
    const phrases = texte
        .split("\n")
        .map(p => p.trim())
        .filter(Boolean);

    for (const phrase of phrases) {

        const res = await fetch("/eval", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ prompt: phrase })
        });

        const data = await res.json();

        console.log("EVAL RESULT :", data.resultats);
    }
}

/* =========================
   EXPORT CSV
========================= */
async function exportCSV() {
    if (tousResultats.length === 0)
        return alert("Pas de résultats à exporter !");

    const models = ["ChatGPT", "Claude", "Deepseek", "Meta AI", "Mistral"];

    let csv = ["ID,Phrase," + models.join(",")];

    tousResultats.forEach(item => {

        const row = [
            item.id,
            `"${escapeCSV(item.phrase)}"`,
            ...models.map(m => `"${escapeCSV(item[m] || "")}"`)
        ];

        csv.push(row.join(","));
    });

    const blob = new Blob([csv.join("\n")], {
        type: "text/csv;charset=utf-8;"
    });

    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");

    a.href = url;
    a.download = "resultats.csv";
    a.click();

    URL.revokeObjectURL(url);
}

/* =========================
   EXPORT LATEX
========================= */
async function exportLatex() {
    if (tousResultats.length === 0)
        return alert("Pas de résultats à exporter !");

    let latex = `
\\begin{longtable}{|c|p{10cm}|}
\\hline
\\endfirsthead
\\hline
\\endhead
\\hline
\\endfoot
`;

    const models = ["ChatGPT", "Claude", "Deepseek", "Meta AI", "Mistral"];

    tousResultats.forEach(item => {

        latex += `${item.id} & ${escapeLatex(item.phrase)} \\\\\n\\hline\n`;

        models.forEach(model => {
            latex += `${model} & \\small ${escapeLatex(item[model] || "")} \\\\\n`;
        });

        latex += `\\hline\n`;
    });

    latex += `\\end{longtable}`;

    const blob = new Blob([latex], {
        type: "text/plain;charset=utf-8;"
    });

    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");

    a.href = url;
    a.download = "resultats.tex";
    a.click();

    URL.revokeObjectURL(url);
}

/* =========================
   UTILS
========================= */
function escapeCSV(text) {
    return String(text || "")
        .replace(/"/g, '""')
        .replace(/\n/g, " ");
}

function escapeLatex(text) {
    return String(text || "")
        .replace(/\\/g, "\\textbackslash{}")
        .replace(/&/g, "\\&")
        .replace(/%/g, "\\%")
        .replace(/\$/g, "\\$")
        .replace(/#/g, "\\#")
        .replace(/_/g, "\\_")
        .replace(/{/g, "\\{")
        .replace(/}/g, "\\}")
        .replace(/\n/g, " ");a
}

function escapeHTML(text) {
    return String(text || "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
}