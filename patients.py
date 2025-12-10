import random

# 25 patient names
NAMES = [
    "John", "Lily", "Mark", "Anna", "Paul", "Sara", "David", "Emily",
    "Christopher", "Ava", "Daniel", "Sophia", "Matthew", "Chloe", "Kyle",
    "Ella", "Lucas", "Grace", "Nathan", "Zoe", "Ryan", "Mia", "Ethan",
    "Olivia", "Noah"
]

# Personalities
PERSONALITIES = ["Calm", "Nervous", "Scared", "Rude", "Angry", "Quiet", "Sassy", "Impatient", "Grateful"]

# Mapping personality to treatment time (seconds)
PERSONALITY_TREATMENT_TIME = {
    "Impatient": 20,
    "Angry": 25,
    "Nervous": 35,
    "Scared": 30,
    "Rude": 25,
    "Quiet": 40,
    "Sassy": 25,
    "Calm": 45,
    "Grateful": 50
}

# Conditions
CONDITIONS = [
    "Flu", "Migraine", "Anxiety Attack", "Food Poisoning",
    "Broken Hand", "Asthma Flare", "Heart Failure", "Sepsis", "Mild Allergic Reaction",
    "Bacterial Infection", "High Blood Pressure", "Bronchitis", "Diabetes",
    "Ketone Acidosis", "COPD Flare", "Pneumonia", "UTI with Fever",
    "Osteoarthritis Flare", "Anaphylactic Shock"
]

def get_random_name():
    return random.choice(NAMES)

def get_random_personality():
    return random.choice(PERSONALITIES)

def get_random_condition():
    return random.choice(CONDITIONS)

class Patient:
    def __init__(self, name, condition, personality, is_angry=False):
        self.name = name
        self.condition = condition
        self.personality = personality
        self.is_angry = is_angry
        self.med_given = None
        self.admitted = False
        # Set treatment time based on personality
        self.treatment_time = PERSONALITY_TREATMENT_TIME.get(personality, 30)  # default 30 seconds
        self.time_left = self.treatment_time
