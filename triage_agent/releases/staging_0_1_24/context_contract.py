"""Small provider schema and safe, field-specific validation errors."""
class ContextValidationError(ValueError):
    def __init__(self, code, field, message):
        super().__init__(message)
        self.code, self.field = code, field


CONTEXT_RESPONSE_FORMAT = {"type": "json_schema", "json_schema": {
    "name": "triage_context", "strict": True, "schema": {
        "type": "object", "additionalProperties": False,
        "required": ["possible_explanations", "recommended_next_steps"],
        "properties": {
            "possible_explanations": {"type": "array", "minItems": 1, "maxItems": 2,
                "items": {"type": "string", "minLength": 1, "maxLength": 300}},
            "recommended_next_steps": {"type": "array", "minItems": 2, "maxItems": 2,
                "items": {"type": "string", "minLength": 1, "maxLength": 300}},
        },
    },
}}
