# risk_engine.py

PERMISSION_WEIGHTS = {
    "INTERNET": 1,
    "CAMERA": 3,
    "MICROPHONE": 4,
    "LOCATION": 4,
    "CONTACTS": 5,
    "SMS": 8,
    "CALL_LOG": 9
}

NORMAL_PERMISSIONS = {
    "INTERNET",
    "CAMERA",
    "MICROPHONE"
}

def calculate_risk(permissions):
    score = 0
    explanations = []

    for perm in permissions:
        weight = PERMISSION_WEIGHTS.get(perm, 2)
        score += weight

        if perm not in NORMAL_PERMISSIONS:
            explanations.append(
                f"{perm} is considered sensitive for social media apps (+{weight})"
            )

    if score < 8:
        level = "LOW"
    elif score < 15:
        level = "MEDIUM"
    else:
        level = "HIGH"

    return score, level, explanations

