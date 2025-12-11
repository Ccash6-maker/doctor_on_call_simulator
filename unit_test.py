"""
unit_test.py — Automated tests for Doctor On Call Simulator.

This test suite validates:
    • Patient class behavior (treatment time, initial values)
    • ClinicMemory (add/reset/save/load/average)
    • evaluate_patient() logic (star rating rules, severe condition rules)

NOTE:
These tests DO NOT require pygame, because they only import and test
pure logic functions and classes. The main game loop is not invoked.

Run with:
    python -m unittest unit_test.py
"""

import unittest
import os
import json

from patients import Patient, PERSONALITY_TREATMENT_TIME
from memory import ClinicMemory
from game import evaluate_patient
from medications import CONDITION_TO_CORRECT_MED, SEVERE_CONDITIONS


class TestPatientClass(unittest.TestCase):
    """Tests for the Patient class and supporting functions."""

    def test_patient_treatment_time_correctly_assigned(self):
        """Ensure each patient personality gets the correct treatment time."""
        for personality, expected_time in PERSONALITY_TREATMENT_TIME.items():
            p = Patient("Test", "Flu", personality)
            self.assertEqual(
                p.treatment_time,
                expected_time,
                msg=f"Personality '{personality}' should give {expected_time}s"
            )

    def test_patient_time_left_initializes_full(self):
        """time_left should begin equal to treatment_time."""
        p = Patient("John", "Flu", "Calm")
        self.assertEqual(p.time_left, p.treatment_time)


class TestClinicMemory(unittest.TestCase):
    """Tests for patient rating memory storage."""

    def test_add_and_average(self):
        """Adding reviews should change the stored average."""
        mem = ClinicMemory()
        mem.add_review(5)
        mem.add_review(3)
        self.assertEqual(mem.get_average_stars(), 4.0)

    def test_reset(self):
        """Reset should clear all stored reviews."""
        mem = ClinicMemory()
        mem.add_review(2)
        mem.add_review(5)
        mem.reset_reviews()
        self.assertEqual(mem.get_average_stars(), 0)

    def test_save_and_load(self):
        """Ensure reviews save to disk and load correctly."""
        filename = "test_reviews.json"
        mem = ClinicMemory()
        mem.add_review(4)
        mem.add_review(1)
        mem.save_to_file(filename)

        # load into new memory instance
        mem2 = ClinicMemory()
        mem2.load_from_file(filename)

        self.assertEqual(mem2.all_reviews, [4, 1])

        # cleanup
        if os.path.exists(filename):
            os.remove(filename)


class TestEvaluatePatient(unittest.TestCase):
    """Tests evaluation logic from evaluate_patient()."""

    # Helper methods 

    def make_patient(self, condition, correct=True, severe=False, admitted=False):
        """
        Quickly build a patient for evaluating.
        correct=True => assigns a correct medication
        severe=True => marks condition as severe
        admitted=True => sets patient as admitted
        """
        p = Patient("Test", condition, "Calm")

        if severe:
            self.assertIn(condition, SEVERE_CONDITIONS)

        if correct:
            p.med_given = CONDITION_TO_CORRECT_MED[condition][0]
        else:
            p.med_given = "INVALID_MED"

        p.admitted = admitted
        return p

    # <<<<<<<<<<< Non-severe condition tests  >>>>>>>>>>>>>>
  
    def test_non_severe_correct_med(self):
        """Correct treatment on non-severe condition should return 4–5 stars."""
        cond = "Flu"  # not severe
        p = self.make_patient(cond, correct=True, severe=False)
        stars, reason = evaluate_patient(p)

        self.assertIn(stars, [4, 5])
        self.assertIsNone(reason)

    def test_non_severe_wrong_med(self):
        """Wrong med → 1–3 stars with a complaint reason."""
        cond = "Flu"
        p = self.make_patient(cond, correct=False)
        stars, reason = evaluate_patient(p)

        self.assertIn(stars, [1, 2, 3])
        self.assertIsNotNone(reason)

    def test_non_severe_no_med(self):
        """Giving no medication at all should yield 1 star."""
        p = Patient("Test", "Flu", "Calm")
        p.med_given = None
        stars, reason = evaluate_patient(p)

        self.assertEqual(stars, 1)
        self.assertIsNone(reason)

    # <<<<<<<<<<< Severe condition tests >>>>>>>>>>>>

    def test_severe_correct_and_admitted(self):
        """Severe condition: correct med + admitted → 4–5 stars."""
        cond = SEVERE_CONDITIONS[0]
        p = self.make_patient(cond, correct=True, severe=True, admitted=True)

        stars, reason = evaluate_patient(p)
        self.assertIn(stars, [4, 5])
        self.assertIsNone(reason)

    def test_severe_missing_admission(self):
        """Severe condition but NOT admitted → catastrophic failure."""
        cond = SEVERE_CONDITIONS[0]
        p = self.make_patient(cond, correct=True, severe=True, admitted=False)

        stars, reason = evaluate_patient(p)

        self.assertEqual(stars, 0)
        self.assertIsNotNone(reason)
        self.assertIn("Clinic Closed", reason)

    def test_severe_wrong_med(self):
        """Severe condition + wrong med → catastrophic 0 stars."""
        cond = SEVERE_CONDITIONS[0]
        p = self.make_patient(cond, correct=False, severe=True, admitted=True)

        stars, reason = evaluate_patient(p)
        self.assertEqual(stars, 0)
        self.assertIn("severe condition", reason.lower())


# Main entry point

if __name__ == "__main__":
    unittest.main()
