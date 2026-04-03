import os
import fitz  # PyMuPDF

def extract_pdf_content(file_path):
    try:
        doc = fitz.open(file_path)
        full_text = ""
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            full_text += f"\n--- Page {page_num + 1} ---\n"
            full_text += text
            full_text += "\n"
        
        doc.close()
        return full_text
    except Exception as e:
        return f"Error reading {file_path}: {str(e)}"

def main():
    pdf_files = [
        ("GiftPedia_Problem", "Docs/GiftPedia_Problem.pdf"),
        ("Agent_Prompt_Design", "Docs/Agent_Prompt_Design_and_Vector_DB_schema.pdf")
    ]
    
    for name, file_path in pdf_files:
        if os.path.exists(file_path):
            print(f"Extracting content from {file_path}...")
            content = extract_pdf_content(file_path)
            
            # Save to a text file for easier reading
            output_file = f"Docs/{name}_extracted.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"Content saved to {output_file}")
            print(f"Total characters: {len(content)}")
        else:
            print(f"File not found: {file_path}")

if __name__ == "__main__":
    main()
