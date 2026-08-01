import json
import logging
from jsonschema import validate, ValidationError

logging.basicConfig(level=logging.INFO)

CAPTION_SCHEMA = {
    "type": "object",
    "properties": {
        "motif": {"type": "string", "description": "Primary design motif (e.g., peacock, mango, geometric, temple)"},
        "palette": {
            "type": "array", 
            "items": {"type": "string"}, 
            "description": "Main colors (e.g., ['emerald green', 'gold'])"
        },
        "weave": {"type": "string", "description": "Type of weave/fabric (e.g., kanjeevaram silk, banarasi, cotton)"},
        "placement": {
            "type": "string", 
            "enum": ["body_tile", "border", "pallu"], 
            "description": "The textile component this image represents"
        },
        "dimensions": {"type": "string", "description": "Approximate physical dimensions for print scale (e.g., 20x20cm repeat)"},
        "repeat_direction": {
            "type": "string", 
            "enum": ["seamless_both", "seamless_horizontal", "seamless_vertical", "none"], 
            "description": "How this component tiles"
        },
        "raw_caption": {"type": "string", "description": "Any additional descriptive text"}
    },
    "required": ["motif", "palette", "weave", "placement", "repeat_direction"]
}

def validate_caption(caption_data: dict) -> bool:
    """Validates if a parsed caption JSON meets the strict schema requirements."""
    try:
        validate(instance=caption_data, schema=CAPTION_SCHEMA)
        return True
    except ValidationError as e:
        logging.error(f"Caption validation failed: {e.message}")
        return False
