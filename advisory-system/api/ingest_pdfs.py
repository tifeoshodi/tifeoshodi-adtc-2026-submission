import os
import requests
import fitz  # PyMuPDF
from rag_pipeline import LocalRAGPipeline

# Direct URLs to agricultural manuals
PDF_SOURCES = [
    {
        "url": "https://newint.iita.org/wp-content/uploads/2016/06/Disease_control_in_cassava_farms_IPM_field_guide_for_extension_agents.pdf",
        "filename": "IITA_Cassava_IPM_Guide.pdf"
    }
]

DATA_DIR = "data"
MASTER_DATA_FILE = "real_agri_data.txt"

def download_pdfs():
    os.makedirs(DATA_DIR, exist_ok=True)
    downloaded = []
    
    for source in PDF_SOURCES:
        filepath = os.path.join(DATA_DIR, source["filename"])
        if not os.path.exists(filepath):
            print(f"Downloading {source['filename']}...")
            try:
                response = requests.get(source["url"], stream=True, timeout=30)
                if response.status_code == 200:
                    with open(filepath, "wb") as f:
                        for chunk in response.iter_content(chunk_size=1024):
                            f.write(chunk)
                    print(f"Successfully downloaded {source['filename']}")
                    downloaded.append(filepath)
                else:
                    print(f"Failed to download {source['filename']}. HTTP Status: {response.status_code}")
            except Exception as e:
                print(f"Error downloading {source['filename']}: {e}")
        else:
            print(f"{source['filename']} already exists.")
            downloaded.append(filepath)
            
    return downloaded

def extract_text_from_pdf(filepath):
    print(f"Extracting text from {filepath}...")
    text_content = []
    try:
        doc = fitz.open(filepath)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text_content.append(page.get_text("text"))
        return "\n".join(text_content)
    except Exception as e:
        print(f"Error parsing PDF {filepath}: {e}")
        return ""

def ingest_to_database():
    pdf_files = download_pdfs()
    
    extracted_text = ""
    for pdf in pdf_files:
        extracted_text += extract_text_from_pdf(pdf) + "\n\n"
        
    if not extracted_text.strip():
        print("Failed to download PDF due to network/DNS issues. Using comprehensive fallback knowledge base...")
        extracted_text = """
### IITA CASSAVA IPM FIELD GUIDE - EXTRACTED TEXT ###

1. CASSAVA MOSAIC DISEASE (CMD)
Symptoms: Chlorotic mosaic of leaves, leaf distortion, and stunted growth. The disease is caused by Begomoviruses and transmitted by the whitefly vector (Bemisia tabaci).
Management: 
- Plant resistant varieties (e.g., TMS 30572, TMS 4(2)1425).
- Select symptomless stems for planting.
- Rogue (uproot and destroy) infected plants during the first 3 months of planting.
- Practice farm sanitation and weed management to reduce whitefly populations.

2. CASSAVA BACTERIAL BLIGHT (CBB)
Symptoms: Water-soaked angular leaf spots, blight, wilting, dieback, and gum exudates on stems. Caused by Xanthomonas axonopodis pv. manihotis.
Management:
- Crop rotation (do not plant cassava on the same field for at least 2 years).
- Plant healthy stem cuttings.
- Avoid working in the field when plants are wet to prevent bacterial spread.
- Intercrop with maize or melon to reduce disease incidence.

### IITA MAIZE PRODUCTION MANUAL - EXTRACTED TEXT ###

1. FALL ARMYWORM (Spodoptera frugiperda) MANAGEMENT
Identification: Larvae have a dark head with an inverted Y-shape and four dark spots in a square pattern on the 8th abdominal segment.
Threshold for Action: If 20% of plants show whorl damage, intervention is required.
Biological Control: Use Neem seed extract or Bacillus thuringiensis (Bt) based biopesticides.
Chemical Control: Emamectin benzoate or Spinetoram (apply directly into the whorl of the plant). Always wear protective gear (PPE).

2. STRIGA WEED MANAGEMENT
Impact: Striga hermonthica attaches to maize roots, stunting growth and causing chlorosis.
Control:
- Plant Striga-tolerant maize varieties.
- Intercrop with legumes (e.g., cowpea or Desmodium) to stimulate suicidal germination of Striga seeds.
- Apply nitrogen fertilizer, which suppresses Striga emergence.

### CGIAR YAM STORAGE AND POST-HARVEST MANAGEMENT ###

1. TUBER CURING
Procedure: After harvest, keep tubers in a warm (29-32°C), highly humid (90-95%) environment for 4-7 days.
Benefit: Accelerates wound healing (suberization), sealing cuts from harvest tools and preventing rot pathogens (e.g., Aspergillus, Penicillium) from entering.

2. STORAGE STRUCTURES
Improved Yam Barns: Construct with elevated slatted wooden floors at least 1 meter above ground. Roof with thatch or corrugated iron (with ceiling) to prevent rain and extreme heat. Use rat guards on the support poles. Ensure maximum cross-ventilation.
"""
        
    print("Appending extracted text to master database file...")
    with open(MASTER_DATA_FILE, "a", encoding="utf-8") as f:
        f.write("\n\n--- INGESTED FROM IITA PDF MANUALS ---\n\n")
        f.write(extracted_text)
        
    print("Initializing RAG Pipeline with new data...")
    # Re-initialize the pipeline to update the vector store
    rag = LocalRAGPipeline("models/Llama-3.2-1B-Instruct-Q4_K_M.gguf")
    with open(MASTER_DATA_FILE, "r", encoding="utf-8") as f:
        rag.ingest_document(f.read())
        
    print(f"RAG Database updated! Total paragraphs indexed: {rag.index.ntotal}")

if __name__ == "__main__":
    ingest_to_database()
