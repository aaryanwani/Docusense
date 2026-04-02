import requests
import json

url = 'http://localhost:8000/analyze'
files = {'file': open('/Users/aaryanwani/Desktop/sample_contract.txt', 'rb')}
print("Sending request to FastAPI...")
response = requests.post(url, files=files)

if response.status_code == 200:
    data = response.json()
    with open('/Users/aaryanwani/.gemini/antigravity/brain/b7bffe75-93a9-4cb7-bac0-6d00414a190f/analysis_results.md', 'w') as f:
        f.write("# DocuSense Analysis Result\n\n")
        f.write(f"**Document Type:** {data.get('document_type')}\n\n")
        f.write("## Entity Extraction\n")
        for k, v in data.get('entities', {}).items():
            f.write(f"- **{k}**: {', '.join(v) if isinstance(v, list) else v}\n")
        f.write("\n## Obligations\n")
        for ob in data.get('obligations', []):
            f.write(f"- {ob}\n")
        f.write("\n## AI Summary (Enterprise Analyst Format)\n\n")
        f.write(data.get('summary', ''))
    print("Success! Wrote to artifact.")
else:
    print(f"Error {response.status_code}: {response.text}")

