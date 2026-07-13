import os
import requests

SOURCES_DIR = r"C:\Users\user\Desktop\ADTC\sources"

# High-quality direct PDF links for expansion
MANUALS = [
    {
        "url": "https://www.fao.org/3/a0323e/a0323e00.pdf",
        "filename": "FAO_Training_Manual_Agriculture_Extension.pdf"
    },
    {
        "url": "https://www.fao.org/3/i3316e/i3316e.pdf",
        "filename": "FAO_Climate_Smart_Agriculture.pdf"
    },
    {
        "url": "https://pdf.usaid.gov/pdf_docs/PNADK458.pdf",
        "filename": "USAID_Banana_Tissue_Culture.pdf"
    }
]

def download_manuals():
    if not os.path.exists(SOURCES_DIR):
        os.makedirs(SOURCES_DIR, exist_ok=True)
        
    print(f"Downloading {len(MANUALS)} additional manuals to {SOURCES_DIR}...")
    
    for manual in MANUALS:
        filepath = os.path.join(SOURCES_DIR, manual["filename"])
        if os.path.exists(filepath):
            print(f"Skipping {manual['filename']}, already exists.")
            continue
            
        print(f"Downloading {manual['filename']}...")
        try:
            # Adding a User-Agent to prevent basic blocks
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            response = requests.get(manual["url"], headers=headers, stream=True, timeout=30)
            
            if response.status_code == 200:
                with open(filepath, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"Success: Saved to {filepath}")
            else:
                print(f"Failed: HTTP {response.status_code} for {manual['url']}")
        except Exception as e:
            print(f"Error downloading {manual['filename']}: {e}")

if __name__ == "__main__":
    download_manuals()
