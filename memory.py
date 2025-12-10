"""
memory.py — Handles persistent storage and tracking of clinic ratings.

This module defines the ClinicMemory class, which stores patient ratings,
calculates averages, and could be extended for saving/loading from disk
using JSON or other formats.
"""

import os  # Provides functions for file paths and directory operations
import json  # Provides functions for JSON serialization/deserialization


class ClinicMemory:
    """
    Stores and manages clinic patient ratings.

    Attributes:
        all_reviews (list of int): Stores star ratings (1–5) for each patient.
    """

    def __init__(self):
        """
        Initialize a ClinicMemory instance with an empty reviews list.
        """
        self.all_reviews = []

    def add_review(self, stars: int):
        """
        Add a new patient rating.

        Args:
            stars (int): Number of stars received for patient treatment (1–5).
        """
        self.all_reviews.append(stars)
        # Could optionally save to disk here if persistence is desired

    def get_average_stars(self) -> float:
        """
        Compute the average rating for all patients stored.

        Returns:
            float: Average star rating. Returns 0 if no ratings are present.
        """
        if len(self.all_reviews) == 0:
            return 0.0
        return sum(self.all_reviews) / len(self.all_reviews)

    def reset_reviews(self):
        """
        Clear all stored patient ratings.
        """
        self.all_reviews = []

    def save_to_file(self, filename: str):
        """
        Save all reviews to a JSON file.

        Args:
            filename (str): Path to the JSON file where ratings will be saved.
        """
        try:
            with open(filename, "w") as f:
                json.dump(self.all_reviews, f)
        except Exception as e:
            print(f"Error saving clinic memory: {e}")

    def load_from_file(self, filename: str):
        """
        Load reviews from a JSON file.

        Args:
            filename (str): Path to the JSON file containing ratings.
        """
        if not os.path.exists(filename):
            # If the file doesn't exist, start with empty reviews
            self.all_reviews = []
            return

        try:
            with open(filename, "r") as f:
                self.all_reviews = json.load(f)
        except Exception as e:
            print(f"Error loading clinic memory: {e}")
            self.all_reviews = []
