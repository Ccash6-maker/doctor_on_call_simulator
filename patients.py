"""
patients.py — Defines patient-related data and helper functions.

This module provides:
- A list of possible patient names, personalities, and conditions.
- Functions to randomly choose a name, personality, and condition.
- A Patient class that holds a patient’s attributes and treatment‑time info.
"""

import random


# 25 possible patient names
NAMES = [
    "John", "Lily", "Mark", "Anna", "Paul", "Sara", "David", "Emily",
    "Christopher", "Ava", "Daniel", "Sophia", "Matthew", "Chloe", "Kyle",
    "Ella", "Lucas", "Grace", "Nathan", "Zoe", "Ryan", "Mia", "Ethan",
    "Olivia", "Noah"
]

# Possible patient personalities
PERSONALITIES = [
    "Calm", "Nervous", "Scared", "Rude",
    "Angry", "Quiet", "Sassy", "Impatient", "Grateful"
]

# Map personality → how many seconds the patient can wait (treatment time limit)
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

# List of possible medical conditions for patients
CONDITIONS = [
    "Flu", "Migraine", "Anxiety Attack", "Food Poisoning",
    "Broken Hand", "Asthma Flare", "Heart Failure", "Sepsis",
    "Mild Allergic Reaction", "Bacterial Infection", "High Blood Pressure",
    "Bronchitis", "Diabetes", "Anaphylatic Shock", "Ketone Acidosis",
    "COPD Flare", "Pneumonia", "UTI with Fever", "Osteoarthritis Flare"
]


# Helper functions for random patient generation


def get_random_name():
    """
    Select and return a random name from the NAMES list.

    Returns:
        str: A randomly chosen patient name.
    """
    return random.choice(NAMES)


def get_random_personality():
    """
    Select and return a random personality from PERSONALITIES.

    Returns:
        str: A randomly chosen personality descriptor.
    """
    return random.choice(PERSONALITIES)


def get_random_condition():
    """
    Select and return a random medical condition from CONDITIONS.

    Returns:
        str: A randomly chosen medical condition.
    """
    return random.choice(CONDITIONS)


# Patient class
class Patient:
    """
    Represents a patient in the clinic simulation.

    Attributes:
        name (str): Patient's name.
        condition (str): Medical condition the patient has.
        personality (str): Personality descriptor affecting behavior/timing.
        med_given (str or None): Medication selected for this patient.
        admitted (bool): Whether patient was admitted to a specialist.
        treatment_time (int): Allowed time (in seconds) to treat patient based on personality.
        time_left (int): Remaining time for treatment (counts down during game).
    """

    def __init__(self, name, condition, personality, is_angry=False):
        """
        Initialize a new Patient instance.

        Args:
            name (str): The patient's name.
            condition (str): The medical condition.
            personality (str): The personality descriptor.
            is_angry (bool, optional): Whether the patient starts angry (not used currently).
                                       Default is False.
        """
        self.name = name
        self.condition = condition
        self.personality = personality
        self.is_angry = is_angry  # placeholder — not used in current logic
        self.med_given = None      # will hold chosen medication later
        self.admitted = False      # whether patient is admitted to specialist

        # Determine how much time we have to treat this patient, based on their personality.
        # If personality not in mapping, default to 30 seconds.
        self.treatment_time = PERSONALITY_TREATMENT_TIME.get(personality, 30)

        # Initialize time left counter to full treatment_time
        self.time_left = self.treatment_time
