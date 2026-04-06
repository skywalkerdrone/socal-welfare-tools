import pypdf
import sys
import io

# Set stdout to handle utf-8 appropriately
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def main():
    pdf_path = "docs/26-1조사연구설계서 양식.pdf"
    reader = pypdf.PdfReader(pdf_path)
    output = []
    for i, page in enumerate(reader.pages):
        output.append(f"--- PAGE {i+1} ---")
        text = page.extract_text()
        if text:
            output.append(text)
        else:
            output.append("[No text extracted from this page]")
        output.append("\n")
    
    # Write to a file with utf-8 encoding
    with open("docs/research_form_raw.txt", "w", encoding='utf-8') as f:
        f.write("\n".join(output))

if __name__ == "__main__":
    main()
