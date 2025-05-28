# app.py
from fastapi import FastAPI, File, UploadFile
import fitz  # PyMuPDF
import re

app = FastAPI()

def extract_money(pdf_bytes):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    matches = re.findall(r"R?\$?\s?\d{1,3}(?:\.\d{3})*,\d{2}", text)
    return matches[0] if matches else None

@app.post("/comparar-valores")
async def comparar_valores(file1: UploadFile = File(...), file2: UploadFile = File(...)):
    pdf1_bytes = await file1.read()
    pdf2_bytes = await file2.read()

    valor1 = extract_money(pdf1_bytes)
    valor2 = extract_money(pdf2_bytes)

    return {
        "valor1": valor1,
        "valor2": valor2,
        "iguais": valor1 == valor2
    }
