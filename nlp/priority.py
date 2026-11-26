import re
from typing import Optional

HIGH_PRIORITY_KEYWORDS = [
    # English safety, health & critical outage terms
    "emergency", "urgent", "immediately", "accident", "danger", "dangerous",
    "hazard", "live wire", "electric shock", "electrocution", "short circuit",
    "sparking", "open manhole", "uncovered manhole", "sewage overflow",
    "drain overflow", "flood", "flooding", "waterlogging", "contaminated water",
    "dirty water", "polluted water", "no water", "water shortage", "hospital",
    "school", "clinic", "epidemic", "dengue", "malaria", "cholera", "outbreak",
    "dead animal", "carcass", "fire", "collapse", "collapsed", "fallen tree",
    "road blocked", "sinkhole", "critical", "severe",
    # Hindi (Devanagari)
    "आपातकालीन", "तुरंत", "खतरा", "खतरनाक", "दुर्घटना", "हादसा",
    "खुला मैनहोल", "मैनहोल", "करंट", "बिजली का तार", "शॉर्ट सर्किट",
    "चिंगारी", "बाढ़", "जलभराव", "गंदा पानी", "दूषित पानी", "पानी नहीं",
    "अस्पताल", "स्कूल", "महामारी", "डेंगू", "मलेरिया", "मृत जानवर",
    "आग", "गिर गया", "पेड़ गिरा", "सड़क धंस", "गंभीर",
    # Hinglish (Roman)
    "turant", "khatra", "khatarnak", "hadsa", "khula manhole", "manhole",
    "current", "bijli ka tar", "baadh", "jalbharav", "ganda pani",
    "ganda paani", "pani nahi", "paani nahi", "mahamari", "mara hua janwar",
    "aag", "gir gaya", "ped gira", "sadak dhans", "gambhir"
]

CRITICAL_UTILITY_CATEGORIES = {
    "Water Supply",
    "Drainage & Sewage",
    "Public Health & Hygiene",
    "Roads & Potholes",
    "Streetlights",
    "Waste & Sanitation",
}

DURATION_PATTERN = re.compile(
    r"(\b([3-9]|[1-9]\d+)\s*(days?|din|dino|dinon|weeks?|hafte|hafton|months?|mahine|mahinon)\b"
    r"|पिछले\s*([3-9]|[1-9]\d+)\s*दिनों"
    r"|हफ्तों से|महीनों से)",
    flags=re.IGNORECASE,
)


def assign_priority(text: str, category: Optional[str] = None) -> str:
    """Assign 'High' or 'Normal' priority based on urgency keywords, duration, and category."""
    if not isinstance(text, str) or not text.strip():
        return "Normal"

    # Administrative certificate requests are always Normal priority
    if category == "Municipal Certificates":
        return "Normal"

    lowered = text.lower()

    # 1. Immediate High priority if any safety, health, or emergency keyword matches
    for kw in HIGH_PRIORITY_KEYWORDS:
        if kw in lowered:
            return "High"

    # 2. High priority if a critical utility/sanitation issue has persisted for 3+ days/weeks
    if (category in CRITICAL_UTILITY_CATEGORIES or category is None) and DURATION_PATTERN.search(lowered):
        return "High"

    return "Normal"
