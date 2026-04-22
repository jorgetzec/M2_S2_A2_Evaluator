import docx
import os
from docx.oxml.ns import qn

def debug_docx_colors_xml(path):
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return
        
    doc = docx.Document(path)
    print(f"--- DOCX COLOR DEBUG (XML): {os.path.basename(path)} ---")
    
    unique_font_vals = set()
    unique_shd_fills = set()
    unique_highlights = set()
    
    for para in doc.paragraphs:
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
                    
    print("\nSUMMARY:")
    print(f"  Unique Highlights: {unique_highlights}")
    print(f"  Unique Shading Fills: {unique_shd_fills}")
    print(f"  Unique Font Color Vals: {unique_font_vals}")

if __name__ == "__main__":
    # Handle the complex filename
    path = "docs/TENA_VILLAFAÑE_EUNICE ABIGAIL_M02S1AI2_“El relato de mi historia”..docx"
    debug_docx_colors_xml(path)
