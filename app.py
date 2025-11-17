import gradio as gr
import re
from transformers import pipeline
from langdetect import detect

# -----------------------------
# Modelo de resumen
# -----------------------------
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

# -----------------------------
# Palabras clave ES
# -----------------------------
pagos_kw_es = [
    "pago","pagará","abonará","fee","monto","importe","tarifa","honorario",
    "remuneración","cuota","valor","factura","transferencia","abono",
    "depósito","salario","bono","comisión","costo"
]

penalizaciones_kw_es = [
    "penalización","multa","interés moratorio","sanción","recargo",
    "compensación","indemnización","daños","costas","perjuicio"
]

obligaciones_kw_es = [
    "deberá","se obliga","tiene la obligación","compromete","cumplir",
    "garantizar","proveer","asegurar","entregar","informar"
]

confidencialidad_kw_es = [
    "confidencialidad","no divulgación","NDA","información sensible",
    "protegida","privada","secreto","restricción","reservada","privilegios"
]

terminacion_kw_es = [
    "terminación","resolución","finalización del contrato","cancelación",
    "vencimiento","rescisión","extinción","conclusión","fin","anulación"
]

riesgos_kw_es = [
    "penalización","multa","interés moratorio","incumplimiento","sanción",
    "recargo","riesgo","daños","coste adicional","responsabilidad"
]

# -----------------------------
# Palabras clave EN (equivalentes)
# -----------------------------
pagos_kw_en = [
    "payment","shall pay","will pay","fee","amount","charge","rate","compensation",
    "remuneration","installment","value","invoice","transfer","deposit","salary",
    "bonus","commission","cost"
]

penalizaciones_kw_en = [
    "penalty","fine","late fee","interest","surcharge","compensation","damages",
    "indemnity","liability","loss"
]

obligaciones_kw_en = [
    "shall","must","is obligated","is required","commits to","comply","ensure",
    "provide","deliver","inform","guarantee"
]

confidencialidad_kw_en = [
    "confidentiality","non-disclosure","NDA","sensitive information",
    "protected","private","secret","restriction","confidential","privileged"
]

terminacion_kw_en = [
    "termination","resolution","end of contract","cancellation","expiration",
    "rescission","extinction","conclusion","end","annulment"
]

riesgos_kw_en = [
    "penalty","fine","late fee","breach","risk","damages","extra cost",
    "liability","responsibility","loss"
]

# -----------------------------
# Función para generar regex
# -----------------------------
def generar_regex_clausula(palabras, ventana=150):
    escaped = [re.escape(w) for w in palabras]
    pattern = r".{0," + str(ventana) + r"}(" + "|".join(escaped) + r").{0," + str(ventana) + r"}"
    return re.compile(pattern, re.IGNORECASE | re.DOTALL)

# -----------------------------
# Función principal de análisis
# -----------------------------
def extract_clauses(texto, lang):

    if lang == "en":
        pagos_kw = pagos_kw_en
        penal_kw = penalizaciones_kw_en
        oblig_kw = obligaciones_kw_en
        confid_kw = confidencialidad_kw_en
        term_kw = terminacion_kw_en
    else:
        pagos_kw = pagos_kw_es
        penal_kw = penalizaciones_kw_es
        oblig_kw = obligaciones_kw_es
        confid_kw = confidencialidad_kw_es
        term_kw = terminacion_kw_es

    patron_pagos = generar_regex_clausula(pagos_kw)
    patron_penal = generar_regex_clausula(penal_kw)
    patron_oblig = generar_regex_clausula(oblig_kw)
    patron_conf = generar_regex_clausula(confid_kw)
    patron_term = generar_regex_clausula(term_kw)

    patron_fecha = re.compile(r"\b(?:\d{1,2}[\/\.-]\d{1,2}[\/\.-]\d{2,4}|\d{4}-\d{2}-\d{2})\b")

    frases = re.split(r'\. |\.\n', texto)
    frases = [f.strip() for f in frases if f.strip()]

    clausulas = {
        "fechas": patron_fecha.findall(texto),
        "pagos": [],
        "penalizaciones": [],
        "obligaciones": [],
        "confidencialidad": [],
        "terminación": [],
    }

    for f in frases:
        if patron_pagos.search(f):
            clausulas["pagos"].append(f)
        if patron_penal.search(f):
            clausulas["penalizaciones"].append(f)
        if patron_oblig.search(f):
            clausulas["obligaciones"].append(f)
        if patron_conf.search(f):
            clausulas["confidencialidad"].append(f)
        if patron_term.search(f):
            clausulas["terminación"].append(f)

    return clausulas, frases


def detectar_riesgos(clausulas, frases, lang):

    riesgos_kw = riesgos_kw_en if lang == "en" else riesgos_kw_es

    riesgos = []
    for f in frases:

        if any(rk.lower() in f.lower() for rk in riesgos_kw):
            if not any(f in clausulas[c] for c in [
                "pagos","penalizaciones","obligaciones","confidencialidad","terminación"
            ]):
                riesgos.append(f)

    if not riesgos:
        riesgos.append("No se detectaron riesgos significativos." if lang == "es" else "No significant risks detected.")

    return riesgos


def normalizar_lista(lst):
    return list(dict.fromkeys(lst))


def analizar_contrato(texto):
    try:
        idioma = detect(texto)
        lang = "es" if idioma == "es" else "en"

        clausulas, frases = extract_clauses(texto, lang)
        riesgos = detectar_riesgos(clausulas, frases, lang)

        resumen_ai = summarizer(texto, max_length=250, min_length=80, do_sample=False)[0]["summary_text"]

        salida = "## 📑 Contract Analysis Report\n" if lang == "en" else "## 📑 Informe de Análisis de Contrato\n"
        salida += ("### 📝 Executive Summary\n" if lang == "en" else "### 📝 Resumen Ejecutivo\n") + resumen_ai + "\n\n"

        salida += ("### 📆 Detected Dates\n- " if lang == "en" else "### 📆 Fechas Detectadas\n- ")
        salida += "\n- ".join(normalizar_lista(clausulas["fechas"]) or ["No dates found." if lang=="en" else "No se encontraron fechas."]) + "\n\n"

        salida += ("### 💰 Payments\n- " if lang=="en" else "### 💰 Pagos / Montos\n- ")
        salida += "\n- ".join(normalizar_lista(clausulas["pagos"]) or ["No payments found." if lang=="en" else "No se encontraron pagos."]) + "\n\n"

        salida += ("### ⚠️ Penalties\n- " if lang=="en" else "### ⚠️ Penalizaciones\n- ")
        salida += "\n- ".join(normalizar_lista(clausulas["penalizaciones"]) or ["No penalties detected." if lang=="en" else "Sin penalizaciones detectadas."]) + "\n\n"

        salida += ("### 📌 Obligations\n- " if lang=="en" else "### 📌 Obligaciones\n- ")
        salida += "\n- ".join(normalizar_lista(clausulas["obligaciones"]) or ["No clear obligations found." if lang=="en" else "No se identificaron obligaciones claras."]) + "\n\n"

        salida += ("### 🔒 Confidentiality\n- " if lang=="en" else "### 🔒 Confidencialidad\n- ")
        salida += "\n- ".join(normalizar_lista(clausulas["confidencialidad"]) or ["No confidentiality clause detected." if lang=="en" else "No se detectó cláusula de confidencialidad."]) + "\n\n"

        salida += ("### ❌ Contract Termination\n- " if lang=="en" else "### ❌ Terminación del Contrato\n- ")
        salida += "\n- ".join(normalizar_lista(clausulas["terminación"]) or ["No termination terms detected." if lang=="en" else "No se identificaron condiciones de terminación."]) + "\n\n"

        salida += ("### 🚨 Potential Risks\n- " if lang=="en" else "### 🚨 Riesgos Potenciales\n- ")
        salida += "\n- ".join(normalizar_lista(riesgos))

        return salida

    except Exception as e:
        return f"Error: {str(e)}"


# -----------------------------
# Interfaz Gradio
# -----------------------------
with gr.Blocks() as demo:
    gr.Markdown("## 🤖 Contract Analyzer / Analizador de Contratos")
    gr.Markdown("Paste a contract text on the left to extract clauses, detect risks, and generate an executive summary.")

    with gr.Row():
        # Columna izquierda (input)
        with gr.Column(scale=1):
            input_text = gr.Textbox(
                label="Contract Text / Texto del Contrato",
                placeholder="Paste the contract here...",
                lines=25
            )
            boton = gr.Button("Analyze / Analizar")

        # Columna derecha (output)
        with gr.Column(scale=1):
            output_text = gr.Markdown()

    boton.click(fn=analizar_contrato, inputs=input_text, outputs=output_text)

demo.launch()
