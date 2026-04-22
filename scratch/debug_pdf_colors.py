import fitz
import os
import sys

def debug_pdf(path):
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return
        
    doc = fitz.open(path)
    print(f"--- PDF INFO: {path} ---")
    print(f"Pages: {len(doc)}")
    
    for i, page in enumerate(doc):
        print(f"\nPAGE {i}:")
        drawings = page.get_drawings()
        print(f"  Drawings count: {len(drawings)}")
        
        colored_drawings = []
        for d in drawings:
            fill = d.get("fill")
            if fill:
                colored_drawings.append(d)
        
        print(f"  Colored drawings: {len(colored_drawings)}")
        for cd in colored_drawings[:10]:
            print(f"    Fill: {cd.get('fill')} Rect: {cd.get('rect')}")
            
        data = page.get_text("dict")
        blocks = data.get("blocks", [])
        print(f"  Text Blocks: {len(blocks)}")
        
        colored_spans = 0
        for b in blocks:
            if b.get("type") == 0:
                for l in b.get("lines", []):
                    for s in l.get("spans", []):
                        color = s.get("color")
                        if color != 0:
                            colored_spans += 1
                            if colored_spans < 10:
                                print(f"    Span Color: {color:06X} Text: [{s.get('text')[:20]}]")
        print(f"  Total non-black spans: {colored_spans}")
    doc.close()

if __name__ == "__main__":
    pdf_path = "/app/docs/LojeroSalazar_Estrella_M02S1AI2.pdf"
    debug_pdf(pdf_path)
