# app.py
from fastapi import FastAPI, File, UploadFile
import fitz  # PyMuPDF
import re

app = FastAPI()

# extracts it but kinda ugly, i can make it better latter
def extract_money(pdf_bytes):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()

    matches = re.findall(r"R?\$?\s?\d{1,3}(?:\.\d{3})*(?:,\d{2})?|\d+(?:,\d{2})?", text)

    return matches[0] if matches else None

# Cleans ugly number
def normalize_money(value_str):
    if not value_str:
        return None
    clean = re.sub(r"[^\d,\.]", "", value_str).replace('.', '').replace(',', '.')
    try:
        return float(clean)
    except ValueError:
        return None

# Comparison just that simple
def compare_numbers(v1, v2):
    if v1 is None or v2 is None:
        return "Could not extract one or both values."
    if v1 > v2:
        return "value1 is greater than value2"
    elif v1 < v2:
        return "value2 is greater than value1"
    else:
        return "the values are equal"

# post function name
@app.post("/compare-values")
async def compare_values(file1: UploadFile = File(...), file2: UploadFile = File(...)):
    pdf1_bytes = await file1.read()
    pdf2_bytes = await file2.read()

    value1_str = extract_money(pdf1_bytes)
    value2_str = extract_money(pdf2_bytes)

    value1 = normalize_money(value1_str)
    value2 = normalize_money(value2_str)

    result = compare_numbers(value1, value2)

    return {
        "value1_raw": value1_str,
        "value2_raw": value2_str,
        "value1_normalized": value1,
        "value2_normalized": value2,
        "comparison": result
    }
