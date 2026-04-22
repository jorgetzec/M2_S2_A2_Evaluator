import docx
import os

def debug_docx_colors(path):
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return
        
    doc = docx.Document(path)
    print(f"--- DOCX COLOR DEBUG: {os.path.basename(path)} ---")
    
    unique_colors = set()
    found_highlights = set()
    
    for i, para in enumerate(doc.paragraphs):
        for run in para.runs:
            # Check font color
            font = run.font
            if font and font.color and font.color.rgb:
                unique_colors.add(str(font.color.rgb))
                if i < 20: # Limit output
                    print(f"P{i} Run: [{run.text[:20]}] Font Color: {font.color.rgb}")
            
            # Check highlight (shading)
            if run.font.highlight_color:
                found_highlights.add(run.font.highlight_color)
                if i < 20:
                    print(f"P{i} Run: [{run.text[:20]}] Highlight: {run.font.highlight_color}")

    print("\nSummary of unique Font Colors (RRGGBB):")
    for c in sorted(list(unique_colors)):
        print(f"  {c}")
        
    print("\nSummary of unique Highlight Enums:")
    for h in found_highlights:
        print(f"  {h}")

if __name__ == "__main__":
    path = "docs/CancholaGomez_Alisson_M02S1AI2.docx"
    debug_docx_colors(path)
