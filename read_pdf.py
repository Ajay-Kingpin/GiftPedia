import os
import sys

def try_read_pdf_with_pypdf2(file_path):
    try:
        import PyPDF2
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text
    except Exception as e:
        return f"PyPDF2 Error: {str(e)}"

def try_read_pdf_with_pdfplumber(file_path):
    try:
        import pdfplumber
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text
    except Exception as e:
        return f"pdfplumber Error: {str(e)}"

def try_read_pdf_with_pymupdf(file_path):
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        return f"PyMuPDF Error: {str(e)}"

def main():
    pdf_files = [
        "Docs/GiftPedia_Problem.pdf",
        "Docs/Agent_Prompt_Design_and_Vector_DB_schema.pdf"
    ]
    
    for pdf_file in pdf_files:
        if os.path.exists(pdf_file):
            print(f"\n=== Reading {pdf_file} ===")
            
            print("\n--- Trying PyPDF2 ---")
            result = try_read_pdf_with_pypdf2(pdf_file)
            if len(result) > 500:
                print(result[:500] + "...")
            else:
                print(result)
            
            print("\n--- Trying pdfplumber ---")
            result = try_read_pdf_with_pdfplumber(pdf_file)
            if len(result) > 500:
                print(result[:500] + "...")
            else:
                print(result)
            
            print("\n--- Trying PyMuPDF ---")
            result = try_read_pdf_with_pymupdf(pdf_file)
            if len(result) > 500:
                print(result[:500] + "...")
            else:
                print(result)
        else:
            print(f"File not found: {pdf_file}")

if __name__ == "__main__":
    main()
