# Implementation Plan - Clean Duplicated JSON Data

The user identified duplicated information in the exported JSON (specifically the list of classified words and detected errors). Analysis of `app.py` and `evaluator.py` confirms that several arrays are being repeated under different keys (e.g., `highlights_detail` vs `segments["highlights"]`, and multiple versions of `orthography_matches`).

## Proposed Changes

### `evaluator.py`

#### [MODIFY] [evaluator.py](file:///d:/CODE/Code3_Coding%20and%20Data/20260318_M02S1AI2_app_evaluador/evaluator.py)
Simplify the `export` logic to avoid re-processing or re-nesting already structured data from `extra`. I will remove the manual reconstruction of `orthography_matches` if it's already provided in a clean format.

### `app.py`

#### [MODIFY] [app.py](file:///d:/CODE/Code3_Coding%20and%20Data/20260318_M02S1AI2_app_evaluador/app.py)
Refactor the construction of the `extra` dictionary to:
1.  Remove `highlights_detail` (redundant with `segments["highlights"]`).
2.  Consolidate `orthography_matches` and `recommendations` into a single clean list.
3.  Combine `fragmentos_para_personalizar` and `segments` into a single `data_segments` structure, avoiding repeating the full story text multiple times.
4.  Ensure `metrics` contains only scalar values or small summary objects, moving detailed lists to a `details` section.

## Implementation Details

### New JSON structure (target):
```json
{
  "cognitivo": { ... },
  "actitudinal": { ... },
  "comunicativo": { ... },
  "pensamiento_critico": { ... },
  "originalidad": { ... },
  "total_score": 85,
  "metadata": {
    "filename": "...",
    "student_name": "...",
    "course": "M2"
  },
  "metrics": {
    "story_word_count": 450,
    "highlights_accuracy": 92,
    "orthography_errors": 2,
    "audio_duration": 150
  },
  "details": {
    "highlights": [ ... ],
    "orthography": [ ... ],
    "transcript": "...",
    "story_text": "..."
  },
  "feedback_support": {
    "suggested_materials": [ ... ],
    "mapeo_phrases": "...",
    "fragmentos": { ... }
  }
}
```

## Verification Plan

### Automated Verification
- Run a script to generate the JSON and verify (using `json.loads`) that specific keys are not duplicated and the size of the JSON is optimized.

### Manual Verification
- Manually inspect the "Visor JSON" in the Streamlit app to ensure readability and completeness.
- Verify that the "Download JSON" functionality still works and produces a valid file.
