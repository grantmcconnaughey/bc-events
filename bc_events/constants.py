ACTOR_TYPE_USER = "user"
ACTOR_TYPE_SERVICE = "service"
ACTOR_TYPE_THIRD_PARTY = "third-party"

EVENT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "action": {"$ref": "#/definitions/EventActionName"},
        "actor": {"$ref": "#/definitions/EventActor"},
        "category": {"$ref": "#/definitions/EventCategoryName"},
        "data": {"additionalProperties": True, "minProperties": 1, "properties": {}, "type": "object"},
        "entity": {"$ref": "#/definitions/EventEntityName"},
    },
    "required": ["category", "action", "entity", "data", "actor"],
    "definitions": {
        "EventActionName": {"minLength": 1, "pattern": "^[A-Z][a-z]+$", "type": "string"},
        "EventActor": {
            "properties": {
                "id": {"type": "string", "minLength": 5},
                "type": {"enum": ["user", "service", "third-party"]},
            },
            "required": ["type", "id"],
            "title": "EventActor",
            "type": "object",
        },
        "EventCategoryName": {"minLength": 1, "pattern": "^[a-z]+$", "type": "string"},
        "EventEntityName": {"minLength": 1, "pattern": "^([A-Z][a-z]+)+$", "type": "string"},
    },
}
