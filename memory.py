# memory.py

import json
import os

class ClinicMemory:
    """Simple in-memory clinic storage with optional file save/load."""

    def __init__(self, file_path="clinic_memory.json"):
        self.file_path = file_path
        self.all_reviews = []
        self.day = 1
        # Load from file if exists
        self.load_memory()

    def add_review(self, stars):
        self.all_reviews.append(stars)

    def get_average_stars(self):
        if len(self.all_reviews) == 0:
            return 0
        return sum(self.all_reviews) / len(self.all_reviews)

    def save_memory(self):
        data = {
            "day": self.day,
            "rating": self.all_reviews
        }
        with open(self.file_path, "w") as f:
            json.dump(data, f)

    def load_memory(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r") as f:
                    data = json.load(f)
                    self.day = data.get("day", 1)
                    self.all_reviews = data.get("rating", [])
            except:
                self.day = 1
                self.all_reviews = []
        else:
            self.day = 1
            self.all_reviews = []
