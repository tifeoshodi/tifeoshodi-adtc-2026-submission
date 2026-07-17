import os
import fitz  # PyMuPDF
import re

SOURCES_DIR = r"C:\Users\user\Desktop\ADTC\sources"
MASTER_DATA_FILE = "real_agri_data.txt"

def clean_text(text):
    """Basic text cleaning for extracted PDF text."""
    # Remove excessive newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Remove weird characters or simple formatting artifacts
    text = text.replace('\x00', '')
    # Strip leading/trailing whitespaces
    return text.strip()

def extract_text_from_pdf(filepath):
    print(f"Extracting text from {filepath}...")
    text_content = []
    try:
        doc = fitz.open(filepath)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text("text")
            if text:
                text_content.append(text)
        
        full_text = "\n".join(text_content)
        return clean_text(full_text)
    except Exception as e:
        print(f"Error parsing PDF {filepath}: {e}")
        return ""

def main():
    if not os.path.exists(SOURCES_DIR):
        print(f"Sources directory not found: {SOURCES_DIR}")
        return

    extracted_text = "### HIGH-QUALITY IITA & CGIAR SOURCE DATA ###\n\n"
    
    files_to_process = [f for f in os.listdir(SOURCES_DIR) if f.lower().endswith(('.pdf', '.txt'))]
    print(f"Found {len(files_to_process)} files to process.")

    for filename in files_to_process:
        filepath = os.path.join(SOURCES_DIR, filename)
        
        if filename.lower().endswith('.txt'):
            with open(filepath, 'r', encoding='utf-8') as f:
                text = clean_text(f.read())
        else:
            text = extract_text_from_pdf(filepath)
            
        if text:
            extracted_text += f"\n\n--- SOURCE: {filename} ---\n\n"
            extracted_text += text

    print(f"Writing {len(extracted_text)} characters to {MASTER_DATA_FILE}...")
    # This intentionally overwrites the file, removing the old synthetic data
    with open(MASTER_DATA_FILE, "w", encoding="utf-8") as f:
        f.write(extracted_text)
        
    print("PDF ingestion complete! The data file has been upgraded.")
    print("Please trigger the rebuild index endpoint or run the script to re-embed the vectors.")

if __name__ == "__main__":
    main()
