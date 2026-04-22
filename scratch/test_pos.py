
import sys
import os

sys.path.append('/app')
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mocking parts of analysis_engine if needed or just importing it
# Since we have volumes in docker, we can just run it.

try:
    from analysis_engine import pos_matches_category
    
    test_cases = [
        ("PRON", "DET", "me", True),
        ("PRON", "ADJ", "me", True),
        ("PRON", "NOUN", "me", False),
        ("PRON", "ADP", "me", False),
        ("PRON", "ADV", "me", False),
        ("PRON", "DET", "Yo", True),
    ]
    
    all_passed = True
    for pos, cat, word, expected in test_cases:
        result = pos_matches_category(pos, cat, word)
        status = "PASS" if result == expected else "FAIL"
        print(f"Testing {word} ({pos}) as {cat}: Result={result}, Expected={expected} -> {status}")
        if result != expected:
            all_passed = False
            
    if all_passed:
        print("\nAll POS matching tests passed!")
    else:
        print("\nSome tests failed.")
        sys.exit(1)

except ImportError as e:
    print(f"Error importing analysis_engine: {e}")
    sys.exit(1)
