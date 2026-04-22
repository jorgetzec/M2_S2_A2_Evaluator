import docx
from file_processor import get_run_color_category

doc = docx.Document('docs/PaniaguaDeNicolas_Sara_M02S1AI2.docx')
found = []
for para in doc.paragraphs:
    for run in para.runs:
        cat = get_run_color_category(run)
        if cat:
            found.append((run.text[:20].strip(), cat))

for text, cat in found[:20]:
    print(f"[{text}] -> {cat}")
