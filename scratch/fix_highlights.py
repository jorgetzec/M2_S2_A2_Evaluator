import re

path = 'file_processor.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Inclusive Mapping (Legacy + Standard, excluding 8 from VERB)
# Standard Mappings:
# 4,11: VERB | 3,2,10,9: NOUN | 7,14: ADJ | 5,6: ADV | 12,13: ADP | 16,15: DET
# Legacy Mappings (User says "worked before"):
# 2,8: VERB | 3,5,9,10: NOUN | 1,7: ADJ | 4: ADV | 11,12: ADP | 13,14,16: DET

new_highlights = """{
        1: "ADJ", 7: "ADJ", 14: "ADJ",           # Amarillos / Beige (Legacy + Std)
        2: "VERB", 4: "VERB", 11: "VERB",        # Verdes (Legacy + Std)
        3: "NOUN", 5: "NOUN", 9: "NOUN", 10: "NOUN", 2: "NOUN", # Azules / Rosas legacy
        4: "ADV", 5: "ADV", 6: "ADV",            # Rosas / Rojos legacy+std
        11: "ADP", 12: "ADP", 13: "ADP",         # Morados / Violets
        13: "DET", 14: "DET", 15: "DET", 16: "DET" # Grises
    }"""

# Use regex to find highlights = { ... } blocks
# We target the two patterns
pattern = r'highlights = \{[^\}]+\}'
new_content = re.sub(pattern, f'highlights = {new_highlights}', content)

with open(path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Highlights updated successfully (Inclusive Map applied).")
