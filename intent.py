def detect_intent(text: str):
    text = text.lower()

    if "slot" in text or "available" in text:
        return "SLOTS"

    if "charge" in text or "price" in text or "fee" in text:
        return "CHARGES"

    if "rush" in text or "busy" in text or "peak" in text:
        return "RUSH"

    if "admin" in text or "manager" in text:
        return "ADMIN"

    return "UNKNOWN"
