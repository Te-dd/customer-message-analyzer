import re
from collections import Counter
import json


CATEGORIES = {
    "billing": [
        "payment", "paid", "refund", "charge", "invoice",
        "bill", "money", "transaction", "overcharged"
    ],
    "delivery": [
        "delivery", "delivered", "shipping", "order",
        "package", "parcel", "arrived", "shipment"
    ],
    "technical_support": [
        "error", "bug", "crash", "login", "password",
        "broken", "not working", "failed", "issue"
    ],
    "product_feedback": [
        "quality", "feature", "suggestion", "feedback",
        "improve", "excellent", "product", "disappointed"
    ],
    "cancellation": [
        "cancel", "cancellation", "unsubscribe",
        "close my account", "stop my subscription"
    ]
}

POSITIVE_WORDS = {
    "good", "great", "excellent", "happy", "love",
    "thank", "helpful", "perfect", "satisfied"
}

NEGATIVE_WORDS = {
    "bad", "terrible", "angry", "unhappy", "hate",
    "disappointed", "broken", "failed", "problem",
    "issue", "frustrated", "worst"
}

URGENT_WORDS = {
    "urgent", "immediately", "emergency", "asap",
    "critical", "now", "serious"
}


def find_category(message):
    text = message.lower()
    scores = {}

    for category, keywords in CATEGORIES.items():
        scores[category] = sum(
            1 for keyword in keywords
            if keyword in text
        )

    best_category = max(scores, key=scores.get)

    if scores[best_category] == 0:
        return "other"

    return best_category


def find_sentiment(message):
    words = set(re.findall(r"\b[a-z']+\b", message.lower()))

    positive = len(words & POSITIVE_WORDS)
    negative = len(words & NEGATIVE_WORDS)

    if positive > negative:
        return "positive"

    if negative > positive:
        return "negative"

    return "neutral"


def find_urgency(message):
    text = message.lower()

    if any(word in text for word in URGENT_WORDS):
        return "high"

    if any(word in text for word in [
        "late", "delay", "refund", "not working",
        "cannot access", "can't access"
    ]):
        return "medium"

    return "low"


def summarize_message(message):
    cleaned = " ".join(message.split())

    # Keep the original message intact if it is short.
    if len(cleaned) <= 100:
        return cleaned

    return cleaned[:97].rsplit(" ", 1)[0] + "..."


def extract_keywords(message, limit=5):
    stop_words = {
        "the", "a", "an", "is", "are", "was", "were",
        "i", "we", "you", "they", "it", "and", "or",
        "to", "for", "of", "in", "on", "my", "me",
        "this", "that", "please", "have", "has", "but"
    }

    words = re.findall(r"\b[a-z']+\b", message.lower())

    keywords = [
        word for word in words
        if word not in stop_words and len(word) > 2
    ]

    counts = Counter(keywords)

    return [word for word, _ in counts.most_common(limit)]


def suggest_action(category):
    actions = {
        "billing": "Review the transaction and resolve the billing concern.",
        "delivery": "Check the order status and provide a delivery update.",
        "technical_support": "Investigate the technical issue and provide troubleshooting steps.",
        "product_feedback": "Record the feedback and review it with the product team.",
        "cancellation": "Verify the request and explain the cancellation process.",
        "other": "Review the message and determine the appropriate response."
    }

    return actions[category]


def validate_input(raw_input):
    if not isinstance(raw_input, str):
        return {
            "success": False,
            "error": "Input must be a JSON string."
        }

    if not raw_input.strip():
        return {
            "success": False,
            "error": "Input cannot be empty."
        }

    try:
        data = json.loads(raw_input)
    except json.JSONDecodeError:
        return {
            "success": False,
            "error": "Invalid JSON format."
        }

    if not isinstance(data, dict):
        return {
            "success": False,
            "error": "JSON must contain an object."
        }

    if "message" not in data:
        return {
            "success": False,
            "error": "Missing required field: message."
        }

    message = data["message"]

    if not isinstance(message, str):
        return {
            "success": False,
            "error": "Message must be a string."
        }

    if not message.strip():
        return {
            "success": False,
            "error": "Message cannot be empty."
        }

    return {
        "success": True,
        "message": message.strip()
    }


def analyze_message(raw_input):
    validated = validate_input(raw_input)

    if not validated["success"]:
        return {"error": validated["error"]}

    message = validated["message"]
    category = find_category(message)

    return {
        "category": category,
        "summary": summarize_message(message),
        "sentiment": find_sentiment(message),
        "urgency": find_urgency(message),
        "keywords": extract_keywords(message),
        "suggested_action": suggest_action(category)
    }
