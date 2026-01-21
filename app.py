# app.py
# Backend (Flask) para analizar titulares: sensacionalismo, vaguedad, comillas sospechosas, etc.

from __future__ import annotations

import re
from typing import Iterable

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


# =========================
# Config / vocabularios
# =========================

ALARM_WORDS = {
    "urgente", "escándalo", "impactante", "increíble", "bomba", "última hora",
    "terror", "pánico", "secreto", "revelado", "exclusiva", "terrible", "horrible",
    "alarmante", "dramático", "drama", "catástrofe", "posible", "polémico", "explosivo", 
    "indignante", "alternativa", "sorprendente", "brutal", "devastador", "alerta", "sabotaje", 
    "advertencia", "destacado", "destacados", "riesgo", "amenaza", "peligroso", "grave", "crítico", 
    "inesperado", "verdad", "potencia"
}

ABSOLUTE_WORDS = {"siempre", "nunca", "jamás", "100%", "nadie", "todos", "ningún", "sin", 
                  "innumerados", "extremo", "extrema", "correcto", "único", "única"}

CLICKBAIT_PATTERNS = [
    r"no vas a creer",
    r"lo que pasó",
    r"te va a (sorprender|impactar)",
    r"testigo directo", 
    r"grave error", 
    r"en estos momentos", 
    r"los expertos alertan", 
    r"el giro inesperado", 
    r"acaba de", 
    r"lo que nadie te contó", 
    r"el motivo oculto", 
    r"el detalle clave", 
    r"la razón por la que", 
    r"esto lo cambia todo", 
    r"esto podría afectar", 
    r"sin hacer nada", 
    r"sin esfuerzo", 
    r"cuando veas",
    r"el final", 
    r"graves consecuencias", 
    r"no te lo vas a creer"
]

HIDING_WORDS = {
    "esto", "esta", "este", "estos", "estas",
    "eso", "esa", "ese", "esos", "esas",
    "aquello", "aquella", "aquel", "aquellos", "aquellas",
    "algo", "alguien", "cosa", "cosas",
    "tal", "tales", "cierto", "cierta", "ciertos", "ciertas",
    "supuesto", "supuesta", "supuestos", "supuestas", "alguna", "alguno", "algunas", "algunos"
}

# Marcadores típicos de cita real (heurística)
QUOTE_ATTRIBUTION_WORDS = {
    "dijo", "dice", "afirmó", "afirma", "aseguró", "asegura", "declaró", "declara",
    "explicó", "explica", "según", "comentó", "comenta", "señaló", "señala",
    "escribió", "escribe", "publicó", "publica", "añadió", "añade"
}

# Intensificadores / prefijos
INTENSIFIER_PREFIXES = ["ultra", "mega", "hiper", "super", "súper", "archi"]


# =========================
# Helpers (texto + métricas)
# =========================

def tokenize(text: str) -> list[str]:
    """Devuelve tokens en minúscula (mantiene acentos y el símbolo %)."""
    return re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9%]+", text.lower())

### Task 1 ###
def caps_ratio(text: str) -> float:
    """
    Compute the proportion of alphabetic characters in `text` that are uppercase.

    Ignores non-letter characters (digits, punctuation, spaces).
    If the input contains no alphabetic characters, returns 0.0.

    Returns:
        A float in [0.0, 1.0] = (# uppercase letters) / (# total letters)
    """
    # your code here
    texto = "Este es tu texto"
    texto = text.strip()
    letters = [c for c in texto if c.isalpha()]
    caps = sum(1 for c in letters if c.isupper())
    if not letters:
        return 0.0
    return caps / len(letters)
    

### Task 2 ###
def count_phrases_or_words(lower_raw: str, words: list[str], vocab: Iterable[str]) -> int:
    """
    Cuenta ocurrencias:
      - si el término tiene espacios (frase), usa substring en lower_raw
      - si es una palabra, usa conteo por tokens
    """
    # your code here
    total = 0
    for palabra in vocab:
        if " " in palabra:
            if palabra in lower_raw:
                total += 1
        else:
            total += words.count(palabra)
    return total

### Task 3 ###
def count_patterns(lower_raw: str, patterns: list[str]) -> int:
    """Cuenta cuántos patrones regex aparecen (al menos una vez cada uno)."""
    # your code here 
    hits = 0
    for pattern in patterns:
        if re.search(pattern, lower_raw):
            hits += 1
    return hits

### Task 4 ###
def count_hiding_words(words: list[str]) -> int:
    """Cuenta palabras comodín/vagas (esto/eso/aquello/algo...)."""
    # your code here
    total = 0
    for hiding_word in HIDING_WORDS:
        total += words.count(hiding_word)
    return total

### Task 5 ###
def count_intensifiers(lower_raw: str, words: list[str]) -> int:
    """
    Cuenta intensificadores como ultra/mega/hiper/súper/re/archi.
      - token exacto ("mega")
      - prefijo pegado o con guion ("megacaro", "ultra-rápido")
    """
    # your code here
    total = 0
    for bmega in INTENSIFIER_PREFIXES:
        total += len(re.findall(rf"\b{bmega}[-]?[a-záéíóúüñ]", lower_raw))
    total += sum(1 for w in words if w in INTENSIFIER_PREFIXES)
    return total

### Task 6 ###
def count_suspicious_quotes(raw: str, lower_raw: str) -> int:
    """
    Heurística de comillas sospechosas:
      - detecta segmentos cortos entre comillas ("palabra", 'dos palabras')
      - solo penaliza si NO hay marcadores de atribución en el texto (dijo/según/etc.)
    """
    # your code here
    total = 0
    if any(a in lower_raw for a in QUOTE_ATTRIBUTION_WORDS):
        return 0
    else:
        matches = re.findall(r'(["\'])([^"\']{1,40})\1', raw) 
        for _, contenido in matches:
            resultado = tokenize(contenido) 
            largor = len(resultado)
            if largor <= 3 and largor >= 1:
                total += 1
    return total





# =========================
# Helpers (scoring)
# =========================

### Task 7 ###
def add_points(score: int, reasons: list[str], condition: bool, points: int, reason: str) -> int:
    """Suma puntos y añade una razón si la condición se cumple."""
    # your code here
    if condition == True and points > 0:
        reasons.append(reason)
        return score + points
    else:
        return score


### Task 8 ###
def label_from_score(score: int) -> str:
    """Convierte score (0–100) en etiqueta. (BAJO, MEDIO, ALTO)"""
    # your code hereç
    if score <= 33 and score >= 0:
        label = "BAJO"
    elif score >= 34 and score <= 74:
        label = "MEDIO"
    elif score >= 75:
        label = "ALTO"
    return label


# =========================
# Core analysis
# =========================

### When tasks finished, let's try to understand what is going on here ###
def analyze(text: str) -> dict:
    raw = text.strip()
    lower_raw = raw.lower()
    words = tokenize(raw)

    # métricas
    exclamations = raw.count("!")
    caps = caps_ratio(raw)
    alarm_count = count_phrases_or_words(lower_raw, words, ALARM_WORDS)
    absolute_count = sum(words.count(w) for w in ABSOLUTE_WORDS)
    clickbait_hits = count_patterns(lower_raw, CLICKBAIT_PATTERNS)
    hiding_count = count_hiding_words(words)
    intensifier_count = count_intensifiers(lower_raw, words)
    suspicious_quotes = count_suspicious_quotes(raw, lower_raw)

    # score + razones
    score = 0
    reasons: list[str] = []

    # Mayúsculas
    score = add_points(score, reasons, caps > 0.25, 100*caps,
                       "Muchas mayúsculas (tono agresivo/sensacionalista).")
    score = add_points(score, reasons, 0.15 < caps <= 0.25, 15,
                       "Bastantes mayúsculas (posible tono sensacionalista).")

    # Exclamaciones
    score = add_points(score, reasons, exclamations > 0, max(20, 4 * exclamations),
                       f"Muchas exclamaciones ({exclamations}).")

    # Alarmistas
    score = add_points(score, reasons, alarm_count > 0, max(30, 20 * alarm_count),
                       f"Palabras/frases alarmistas detectadas: {alarm_count}.")

    # Absolutas
    score = add_points(score, reasons, absolute_count > 0, max(20, 15 * absolute_count),
                       f"Afirmaciones absolutas detectadas: {absolute_count}.")

    # Clickbait
    score = add_points(score, reasons, clickbait_hits > 0, 30 * clickbait_hits,
                       "Frases típicas de clickbait detectadas.")

    # Vagueza / ocultación
    score = add_points(score, reasons, hiding_count > 0, max(10, 4 * hiding_count),
                       f"Lenguaje vago/comodín (esto/eso/aquello/algo…): {hiding_count}.")

    # Intensificadores
    score = add_points(score, reasons, intensifier_count > 0, max(15, 6 * intensifier_count),
                       f"Intensificadores/exageración (ultra/mega/hiper/súper…): {intensifier_count}.")

    # Comillas sospechosas
    score = add_points(score, reasons, suspicious_quotes > 0, max(15, 8 * suspicious_quotes),
                       f"Comillas potencialmente irónicas/no textuales: {suspicious_quotes}.")
    
    # largor 

    score_length = round(abs(len(words) - 15))
    if score_length > 4: 
        score += 5 * score_length
        reasons.append(f"Largor sospechozo.")


    # clamp
    score = min(100, score)
    label = label_from_score(score)

    if not reasons:
        reasons.append("No se detectaron señales fuertes de sensacionalismo (según reglas simples).")

    return {
        "score": score,
        "label": label,
        "reasons": reasons,
        "metrics": {
            "caps_ratio": round(caps, 3),
            "exclamation_count": exclamations,
            "alarm_count": alarm_count,
            "absolute_count": absolute_count,
            "clickbait_hits": clickbait_hits,
            "hiding_count": hiding_count,
            "intensifier_count": intensifier_count,
            "suspicious_quotes": suspicious_quotes,
            "length_words": len(words),
        },
        "tips": [
            "¿Qué fuente lo publica? ¿Es confiable?",
            "¿Hay otra fuente independiente que lo confirme?",
            "¿El titular coincide con el contenido completo?"
        ]
    }


# =========================
# Flask routes
# =========================

### Only to run the server, can ignore ###
@app.get("/")
def home():
    return render_template("index.html")

@app.get("/health")
def health():
    return jsonify({"ok": True})


@app.post("/analyze")
def analyze_route():
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()

    if not text:
        return jsonify({"error": "Texto vacío. Pega un titular o una frase."}), 400
    if len(text) > 5000:
        return jsonify({"error": "Texto demasiado largo (máx. 5000 caracteres)."}), 400

    return jsonify(analyze(text))


if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5000, debug=True)






