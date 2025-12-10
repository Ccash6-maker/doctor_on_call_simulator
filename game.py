"""
game.py — Main game logic for Doctor On Call Simulator.

This module handles:
- Setting up the game window and Pygame initialization
- Main game loop: patient generation, timing, UI drawing, event handling
- Selecting medications, admitting to specialist, finishing care
- Evaluating patient treatment and calculating star ratings
- Day progression (5 patients/day, up to Day 3), end-of-day and end-of-game logic
- Displaying messages, game over, and clinic success screens
"""

import pygame
import sys
import random

from patients import Patient, get_random_name, get_random_condition, get_random_personality
from medications import ALL_MEDICATIONS, CONDITION_TO_CORRECT_MED, SEVERE_CONDITIONS
from memory import ClinicMemory

# Initialize Pygame modules
pygame.init()

# Screen setup
WIDTH, HEIGHT = 900, 650
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Doctor On Call Simulator")

# Color constants (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (80, 150, 255)
GREEN = (0, 200, 0)
RED = (200, 50, 50)
DARK_GREY = (100, 100, 100)

# Font setup
FONT = pygame.font.SysFont("arial", 24)
BIG_FONT = pygame.font.SysFont("arial", 34, bold=True)
TITLE_FONT = pygame.font.SysFont("arial", 28, bold=True)

# Load or initialize memory for saving day/rating data
memory = ClinicMemory()

# Global game state
day = 1               # Current day number (1-based)
total_rating = []     # List storing star ratings for all treated patients

# Frame rate controller
clock = pygame.time.Clock()


def draw_text(text, x, y, color=BLACK, font=FONT):
    """
    Draw the given text onto the game window at (x, y) coordinates.

    Args:
        text (str): The string to render.
        x (int): X-coordinate (pixels) on window.
        y (int): Y-coordinate (pixels) on window.
        color (tuple): RGB color tuple for the text.
        font (pygame.font.Font): Font object to render text.
    """
    WIN.blit(font.render(text, True, color), (x, y))


def generate_patient():
    """
    Create and return a new random Patient object.

    Randomly chooses a name, condition, and personality.
    No memory of past patients is carried over.

    Returns:
        Patient: A new patient instance.
    """
    name = get_random_name()
    cond = get_random_condition()
    personality = get_random_personality()
    return Patient(name, cond, personality)


def evaluate_patient(patient):
    """
    Determine how well the patient was treated, returning star rating and (if any) error reason.

    Logic:
    - Look up correct medications for patient's condition.
    - If patient has a severe condition: require both correct med AND admission to specialist.
      - If that fails → 0 stars and clinic closes.
    - If non-severe:
      - correct medication → 4 or 5 stars
      - wrong medication → 1–3 stars
      - no medication (e.g. timeout) → 1 star by caller logic

    Args:
        patient (Patient): The patient to evaluate.

    Returns:
        (int, str or None): A tuple (stars_awarded, error_reason)
            stars_awarded: number of stars (0–5)
            error_reason: None if OK; otherwise a string explaining clinic closure
    """
    correct_meds = CONDITION_TO_CORRECT_MED.get(patient.condition, [])
    gave_correct_med = patient.med_given in correct_meds

    severe = patient.condition in SEVERE_CONDITIONS
    if severe:
        if patient.admitted and gave_correct_med:
            stars = random.randint(4, 5)
            return stars, None
        reason = (
            f"{patient.name} had a severe condition.\n"
            "Improper care led to complications.\n"
            "Family sued — Clinic Closed."
        )
        return 0, reason

    # Non-severe condition handling
    if gave_correct_med:
        stars = random.randint(4, 5)
        return stars, None
    elif patient.med_given:
        stars = random.randint(1, 3)
        return stars, f"Patient {patient.name} reported poor treatment."
    else:
        # Caller (timeout handling) gives 1 star
        return 1, None


def show_timed_message(lines):
    """
    Draw a blue message box at the bottom-left of the screen with given lines of text.

    Args:
        lines (list of str): Each string is a separate line to display.
    """
    box_w = 400
    box_h = 100
    box_x = 20
    box_y = HEIGHT - box_h - 20

    pygame.draw.rect(WIN, BLUE, (box_x, box_y, box_w, box_h))
    pygame.draw.rect(WIN, BLACK, (box_x, box_y, box_w, box_h), 3)

    offset = 10
    for line in lines:
        draw_text(line, box_x + 10, box_y + offset, (255,255,255))
        offset += 28


def title_screen():
    """
    Display the title screen and wait for the user to click anywhere to start the game.

    Shows game title, short instructions, and 'Click Anywhere to Begin'.
    """
    while True:
        WIN.fill(WHITE)
        draw_text("Doctor On Call Simulator", 240, 80, BLUE, BIG_FONT)

        desc = [
            "Treat 5 patients per day",
            "Personalities affect treatment time — stay sharp!",
            "Reach Day 3 with a rating of 3 stars or greater",
            "to prove your clinic deserves to stay open."
        ]

        y = 180
        for line in desc:
            draw_text(line, 120, y, BLACK, FONT)
            y += 40

        start_text = TITLE_FONT.render("Click Anywhere to Begin", True, RED)
        WIN.blit(start_text, (260, 480))

        pygame.display.update()

        # Handle events: quit or mouse click to start
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                return  # Exit title screen and start game


def main():
    """
    Main game loop.

    - Runs title screen.
    - Loops through patients (5 per day).
    - Manages timing, input handling, UI drawing.
    - Evaluates each patient and accumulates ratings.
    - After 3 days (or earlier if clinic closes), shows summary or game over.
    """
    global day, total_rating

    title_screen()

    patients_treated = 0  # Counter for how many patients treated in current day

    # Create first patient
    patient = generate_patient()
    timer_start = pygame.time.get_ticks()
    time_left = patient.time_left  # initial time left based on personality

    selected_med = None
    show_message = None  # Used to display temporary info/status

    while True:
        WIN.fill(WHITE)
        clock.tick(60)  # Limit to 60 FPS

        # Update timer countdown
        elapsed = (pygame.time.get_ticks() - timer_start) // 1000
        time_left = max(patient.time_left - elapsed, 0)

        # If time runs out before finishing care
        if time_left <= 0:
            # Timeout consequence: 1 star, auto-care by senior doctor
            show_message = [
                f"Time ran out treating {patient.name}.",
                "A senior doctor stepped in to finish care."
            ]
            total_rating.append(1)  # Timeout penalty
            pygame.display.update()
            pygame.time.delay(1400)

            patients_treated += 1

            # End-of-day logic if all patients done
            if patients_treated >= 5:
                day += 1
                if day > 3:
                    # NEW: Compute overall average to determine success or closure
                    overall_avg = sum(total_rating) / len(total_rating)
                    WIN.fill(WHITE)
                    if overall_avg >= 3:
                        draw_text("You have proven this clinic deserves to stay open!", 120, 250, BLUE, BIG_FONT)
                        draw_text(f"Final Rating: {overall_avg:.2f} stars", 260, 310, BLUE, BIG_FONT)
                        draw_text("Congratulations!", 350, 360, BLUE, BIG_FONT)
                    else:
                        draw_text("The clinic received too many complaints.", 150, 250, RED, BIG_FONT)
                        draw_text(f"Final Rating: {overall_avg:.2f} stars", 260, 310, RED, BIG_FONT)
                        draw_text("The clinic has been closed.", 270, 360, RED, BIG_FONT)

                    pygame.display.update()
                    pygame.time.delay(3500)
                    pygame.quit()
                    sys.exit()

                # Show end-of-day summary
                WIN.fill(WHITE)
                draw_text(f"End of Day {day-1}", 330, 200, RED, BIG_FONT)
                avg = sum(total_rating[-5:]) / 5
                draw_text(f"Average Rating: {avg:.2f} stars", 300, 250, BLACK, BIG_FONT)
                pygame.display.update()
                pygame.time.delay(3000)

                patients_treated = 0

            # Prepare next patient
            patient = generate_patient()
            timer_start = pygame.time.get_ticks()
            selected_med = None
            show_message = None
            continue  # Skip the rest and start next frame

        # --- Draw UI for current patient and treatment options ---

        # Display patient info and timer
        draw_text(f"Day: {day}", 20, 20, BLACK, BIG_FONT)
        draw_text(f"Patient: {patient.name}", 20, 80)
        draw_text(f"Condition: {patient.condition}", 20, 120)
        draw_text(f"Personality: {patient.personality}", 20, 160)
        draw_text(f"Time Left: {time_left}s", 20, 200, RED)

        # Draw right-side blue box housing treatment buttons
        box_x, box_y, box_w, box_h = 500, 50, 360, HEIGHT - 100
        pygame.draw.rect(WIN, BLUE, (box_x, box_y, box_w, box_h))
        pygame.draw.rect(WIN, BLACK, (box_x, box_y, box_w, box_h), 3)

        # Compute button layout
        button_height = 40
        button_spacing = 10
        buttons_area_height = 2 * button_height + button_spacing + 20
        med_area_height = box_h - buttons_area_height - 20
        med_y = box_y + 20
        spacing = med_area_height // len(ALL_MEDICATIONS)

        # Render medication buttons
        med_buttons = []
        for med in ALL_MEDICATIONS:
            rect = pygame.Rect(box_x + 20, med_y, box_w - 40, 35)
            pygame.draw.rect(WIN, DARK_GREY, rect)
            pygame.draw.rect(WIN, BLACK, rect, 2)
            draw_text(med, rect.x + 10, rect.y + 5, WHITE)
            med_buttons.append((rect, med))
            med_y += spacing

        # Render "Admit to Specialist" button
        admit_rect = pygame.Rect(box_x + 20, box_y + box_h - buttons_area_height, box_w - 40, button_height)
        pygame.draw.rect(WIN, RED, admit_rect)
        draw_text("Admit to Specialist", admit_rect.x + 10, admit_rect.y + 5, WHITE)

        # Render "Finish Care" button
        finish_rect = pygame.Rect(box_x + 20, box_y + box_h - button_height - 10, box_w - 40, button_height)
        pygame.draw.rect(WIN, GREEN, finish_rect)
        draw_text("Finish Care", finish_rect.x + 10, finish_rect.y + 5, WHITE)

        # If there's a temporary message (e.g. med selected or timeout warning), show it
        if show_message:
            show_timed_message(show_message)

        pygame.display.update()

        # --- Handle events (clicks / quit) ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()

                # Check if a medication button was clicked
                for rect, med in med_buttons:
                    if rect.collidepoint(mx, my):
                        patient.med_given = med
                        show_message = [f"Selected: {med}"]
                        break  # Only one med selection at a time

                # Check if "Admit to Specialist" clicked
                if admit_rect.collidepoint(mx, my):
                    patient.admitted = True
                    show_message = [f"{patient.name} has been admitted."]

                # Check if "Finish Care" clicked
                if finish_rect.collidepoint(mx, my):
                    stars, reason = evaluate_patient(patient)

                    if stars == 0:
                        # Catastrophic error: clinic closes — show message, then exit
                        WIN.fill(WHITE)
                        y = 200
                        for line in reason.split("\n"):
                            draw_text(line, 100, y, RED)
                            y += 40
                        pygame.display.update()
                        pygame.time.delay(3500)
                        pygame.quit()
                        sys.exit()

                    # Valid patient treatment: record stars
                    total_rating.append(stars)

                    patients_treated += 1

                    if patients_treated >= 5:
                        day += 1
                        if day > 3:
                            # NEW: Compute overall average to determine success or closure
                            overall_avg = sum(total_rating) / len(total_rating)
                            WIN.fill(WHITE)
                            if overall_avg >= 3:
                                draw_text("You have proven this clinic deserves to stay open!", 120, 250, BLUE, BIG_FONT)
                                draw_text(f"Final Rating: {overall_avg:.2f} stars", 260, 310, BLUE, BIG_FONT)
                                draw_text("Congratulations!", 350, 360, BLUE, BIG_FONT)
                            else:
                                draw_text("The clinic received too many complaints.", 150, 250, RED, BIG_FONT)
                                draw_text(f"Final Rating: {overall_avg:.2f} stars", 260, 310, RED, BIG_FONT)
                                draw_text("The clinic has been closed.", 270, 360, RED, BIG_FONT)

                            pygame.display.update()
                            pygame.time.delay(3500)
                            pygame.quit()
                            sys.exit()

                        # Show end-of-day summary for last 5 patients
                        WIN.fill(WHITE)
                        draw_text(f"End of Day {day-1}", 330, 200, RED, BIG_FONT)
                        avg = sum(total_rating[-5:]) / 5
                        draw_text(f"Average Rating: {avg:.2f} stars", 300, 250, BLACK, BIG_FONT)
                        y_rating = 320
                        for i, s in enumerate(total_rating[-5:]):
                            draw_text(f"Patient {i+1}: {s} stars", 300, y_rating, BLACK, FONT)
                            y_rating += 30
                        pygame.display.update()
                        pygame.time.delay(3000)

                        patients_treated = 0

                    # Proceed to next patient
                    patient = generate_patient()
                    timer_start = pygame.time.get_ticks()
                    selected_med = None
                    show_message = None


if __name__ == "__main__":
    main()
