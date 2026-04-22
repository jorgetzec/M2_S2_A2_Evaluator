import docx
import os
from docx.oxml.ns import qn

def debug_docx_colors_detailed(path):
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return
        
    doc = docx.Document(path)
    print(f"--- DOCX COLOR DEBUG: {os.path.basename(path)} ---")
    
    for i, para in enumerate(doc.paragraphs[:30]): # Check first 30 paras
        # Check Paragraph Shading (pPr/shd)
        pPr = para._element.get_or_add_pPr()
        p_shd = pPr.xpath('w:shd')
        p_fill = None
        if p_shd:
            p_fill = p_shd[0].get(qn('w:fill'))
            
        print(f"\nP{i}: [{para.text[:50]}...]")
        if p_fill and p_fill != 'auto':
            print(f"  Paragraph Shading: {p_fill}")
            
        for j, run in enumerate(para.runs):
            rPr = run._element.get_or_add_rPr()
            
            # 1. Highlight
            hl = run.font.highlight_color
            
            # 2. Run Shading (rPr/shd)
            shd = rPr.xpath('w:shd')
            fill = None
            if shd:
                fill = shd[0].get(qn('w:fill'))
            
            # 3. Color
            color_elem = rPr.find(qn('w:color'))
            val = None
            if color_elem is not None:
                val = color_elem.get(qn('w:val'))
            
            if hl or (fill and fill != 'auto') or (val and val.upper() not in ('000000', 'AUTO')):
                token = run.text.strip()
                if token:
                    print(f"    R{j} [{token[:20]}]: HL={hl}, SHD={fill}, COLOR={val}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = "docs/_Alarcon Sanchez _jimena _M02S1AI2   .docx"
    debug_docx_colors_detailed(path)
