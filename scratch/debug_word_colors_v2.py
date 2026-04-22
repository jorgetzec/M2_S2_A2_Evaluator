import docx
import os
from docx.oxml.ns import qn
import re

def debug_docx_colors_xml(path):
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return
        
    doc = docx.Document(path)
    print(f"--- DOCX COLOR DEBUG (XML): {os.path.basename(path)} ---")
    
    unique_font_vals = set()
    unique_shd_fills = set()
    unique_highlights = set()
    
    for i, para in enumerate(doc.paragraphs):
        for run in para.runs:
            rPr = run._element.get_or_add_rPr()
            
            # 1. Highlight
            hl = run.font.highlight_color
            if hl:
                unique_highlights.add(hl)
            
            # 2. Shading
            shd = rPr.xpath('w:shd')
            if shd:
                fill = shd[0].get(qn('w:fill'))
                if fill and fill != 'auto':
                    unique_shd_fills.add(fill)
            
            # 3. Font color val
            color_elem = rPr.find(qn('w:color'))
            if color_elem is not None:
                val = color_elem.get(qn('w:val'))
                if val:
                    unique_font_vals.add(val)
                    
            # Print samples if colored
            if hl or shd or (color_elem is not None):
                if i < 30:
                    text_snippet = run.text[:20].strip()
                    if text_snippet:
                        print(f"P{i} [{text_snippet}]: HL={hl}, SHD={unique_shd_fills}, VAL={color_elem.get(qn('w:val')) if color_elem is not None else None}")

    print("\nSUMMARY:")
    print(f"  Unique Highlights: {unique_highlights}")
    print(f"  Unique Shading Fills: {unique_shd_fills}")
    print(f"  Unique Font Color Vals: {unique_font_vals}")

if __name__ == "__main__":
    path = "docs/CancholaGomez_Alisson_M02S1AI2.docx"
    debug_docx_colors_xml(path)
