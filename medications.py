ALL_MEDICATIONS = [
    "Tylenol",
    "Antibiotics",
    "Inhaler",
    "Tamiflu",
    "Beta Blocker",
    "IV Fluids",
    "Anxiety Sedative",
    "Triptan",
    "Eipnephrine",
    "Bronchodilator",
    "Insulin Drip",
    "Anti-inflammatory"
]

# Mapping conditions → list of correct medications
CONDITION_TO_CORRECT_MED = {
    "Flu": ["Tamiflu"],
    "Migraine": ["Triptan"],
    "Anxiety Attack": ["Anxiety Sedative"],
    "Food Poisoning": ["IV Fluids"],
    "Broken Hand": ["Tylenol"],
    "Asthma Flare": ["Inhaler"],
    "Mild Allergic Reaction": ["Eipnephrine"],
    "Bacterial Infection": ["Antibiotics"],
    "High Blood Pressure": ["Beta Blocker"],
    "Bronchitis": ["Bronchodilator"],
    "Diabetes": ["Insulin Drip"],
    "COPD Flare": ["Inhaler", "Bronchodilator"],
    "Pneumonia": ["Antibiotics", "IV Fluids"],
    "UTI with Fever": ["Antibiotics", "IV Fluids"],
    "Osteoarthritis Flare": ["Tylenol", "Anti-inflammatory"],

    # Severe conditions require med + admit
    "Heart Failure": ["Beta Blocker"],
    "Sepsis": ["Antibiotics"],
    "Anaphylactic Shock": ["Eipnephrine", "IV Fluids"],
    "Ketone Acidosis": ["Insulin Drip", "IV Fluids"],
}

# Define severe conditions so it can be imported in game.py
SEVERE_CONDITIONS = ["Heart Failure", "Sepsis", "Anaphylactic Shock", "Ketone Acidosis"]
