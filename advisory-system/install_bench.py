import urllib.request
import json
import os

print("Fetching latest llama.cpp release...")
req = urllib.request.Request('https://api.github.com/repos/ggerganov/llama.cpp/releases/latest')
with urllib.request.urlopen(req) as response:
    data = json.loads(response.read())
    
url = None
for asset in data['assets']:
    if 'ubuntu' in asset['name'] and 'x64' in asset['name'] and '.tar.gz' in asset['name']:
        url = asset['browser_download_url']
        break

if not url:
    print("Could not find ubuntu-x64 release!")
    exit(1)

print(f"Downloading {url}...")
os.system(f"wget -qO llama.tar.gz {url}")
print("Extracting llama-bench...")
os.system("mkdir -p llama_tmp && tar -xzf llama.tar.gz -C llama_tmp")
os.system("find llama_tmp -name 'llama-bench' -exec cp {} ~/.local/bin/ \\;")
os.system("chmod +x ~/.local/bin/llama-bench")
os.system("rm -rf llama.tar.gz llama_tmp")
print("Done! llama-bench installed to ~/.local/bin/")
