import pygame
import sys
import random
from patients import Patient, get_random_name, get_random_condition, get_random_personality
from medications import ALL_MEDICATIONS, CONDITION_TO_CORRECT_MED, SEVERE_CONDITIONS
from memory import ClinicMemory

pygame.init()

# Screen setup
WIDTH, HEIGHT = 900, 650
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Doctor On Call Simulator")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (80, 150, 255)
GREEN = (0, 200, 0)
RED = (200, 50, 50)
DARK_GREY = (100, 100, 100)

# Fonts
FONT = pygame.font.SysFont("arial", 24)
BIG_FONT = pygame.font.SysFont("arial", 34, bold=True)
TITLE_FONT = pygame.font.SysFont("arial", 28, bold=True)

# Game memory
memory = ClinicMemory()
day = 1
total_rating = []

# FPS
clock = pygame.time.Clock()


def draw_text(text, x, y, color=BLACK, font=FONT):
    WIN.blit(font.render(text, True, color), (x, y))


def generate_patient():
    """Creates a new patient with random name, condition, and personality."""
    name = get_random_name()
    cond = get_random_condition()
    personality = get_random_personality()
    return Patient(name, cond, personality)


def evaluate_patient(patient):
    """Determine star rating based on treatment correctness."""
    correct_meds = CONDITION_TO_CORRECT_MED.get(patient.condition, [])
    gave_correct_med = patient.med_given in correct_meds

    severe = patient.condition in SEVERE_CONDITIONS
    if severe:
        if patient.admitted and gave_correct_med:
            stars = random.randint(4, 5)
            return stars, None
        reason = (
            f"{patient.name} had a severe condition.\n"
            f"Improper care led to complications.\n"
            f"Family sued — Clinic Closed."
        )
        return 0, reason

    # Non-severe conditions
    if gave_correct_med:
        stars = random.randint(4, 5)
        return stars, None
    elif patient.med_given:
        stars = random.randint(1, 3)
        return stars, f"Patient {patient.name} reported poor treatment."
    else:
        return 1, None  # Time ran out


def show_timed_message(lines):
    """Shows a multi-line message in the bottom-left corner."""
    box_w = 400
    box_h = 100
    box_x = 20
    box_y = HEIGHT - box_h - 20

    pygame.draw.rect(WIN, BLUE, (box_x, box_y, box_w, box_h))
    pygame.draw.rect(WIN, BLACK, (box_x, box_y, box_w, box_h), 3)

    offset = 10
    for line in lines:
        draw_text(line, box_x + 10, box_y + offset, WHITE)
        offset += 28


def title_screen():
    """Launch title screen."""
    running = True
    while running:
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

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                return


def main():
    global day, total_rating

    title_screen()

    patients_treated = 0

    # Generate first patient
    patient = generate_patient()
    timer_start = pygame.time.get_ticks()
    time_left = patient.time_left

    selected_med = None
    show_message = None

    running = True
    while running:
        WIN.fill(WHITE)
        clock.tick(60)

        # Timer logic
        elapsed = (pygame.time.get_ticks() - timer_start) // 1000
        time_left = max(patient.time_left - elapsed, 0)

        # Auto-trigger timeout consequences
        if time_left <= 0:
            show_message = [
                f"Time ran out treating {patient.name}.",
                "A senior doctor stepped in to finish care."
            ]
            total_rating.append(1)  # Timeout = 1 star
            pygame.display.update()
            pygame.time.delay(1400)

            patients_treated += 1
            if patients_treated >= 5:
                day += 1
                if day > 3:
                    WIN.fill(WHITE)
                    draw_text("You have proven this clinic deserves to stay open!", 120, 250, BLUE, BIG_FONT)
                    draw_text("Congratulations!", 350, 320, BLUE, BIG_FONT)
                    pygame.display.update()
                    pygame.time.delay(3500)
                    pygame.quit()
                    sys.exit()

                # End of day display
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

            patient = generate_patient()
            timer_start = pygame.time.get_ticks()
            selected_med = None
            show_message = None
            continue

        # Patient info
        draw_text(f"Day: {day}", 20, 20, BLACK, BIG_FONT)
        draw_text(f"Patient: {patient.name}", 20, 80)
        draw_text(f"Condition: {patient.condition}", 20, 120)
        draw_text(f"Personality: {patient.personality}", 20, 160)
        draw_text(f"Time Left: {time_left}s", 20, 200, RED)

        # Right-side blue box for medications
        box_x, box_y, box_w, box_h = 500, 50, 360, HEIGHT - 100
        pygame.draw.rect(WIN, BLUE, (box_x, box_y, box_w, box_h))
        pygame.draw.rect(WIN, BLACK, (box_x, box_y, box_w, box_h), 3)

        # Admit and Finish buttons height
        button_height = 40
        button_spacing = 10
        buttons_area_height = 2 * button_height + button_spacing + 20  # bottom space

        # Medication buttons area
        med_area_height = box_h - buttons_area_height - 20  # top padding
        med_y = box_y + 20
        spacing = med_area_height // len(ALL_MEDICATIONS)

        med_buttons = []
        for med in ALL_MEDICATIONS:
            rect = pygame.Rect(box_x + 20, med_y, box_w - 40, 35)
            pygame.draw.rect(WIN, DARK_GREY, rect)
            pygame.draw.rect(WIN, BLACK, rect, 2)
            draw_text(med, rect.x + 10, rect.y + 5, WHITE)
            med_buttons.append((rect, med))
            med_y += spacing

        # Admit and Finish buttons at bottom of box
        admit_rect = pygame.Rect(box_x + 20, box_y + box_h - buttons_area_height, box_w - 40, button_height)
        pygame.draw.rect(WIN, RED, admit_rect)
        draw_text("Admit to Specialist", admit_rect.x + 10, admit_rect.y + 5, WHITE)

        finish_rect = pygame.Rect(box_x + 20, box_y + box_h - button_height - 10, box_w - 40, button_height)
        pygame.draw.rect(WIN, GREEN, finish_rect)
        draw_text("Finish Care", finish_rect.x + 10, finish_rect.y + 5, WHITE)

        # Popup message
        if show_message:
            show_timed_message(show_message)

        pygame.display.update()

        # Event loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()

                # Medication clicks
                for rect, med in med_buttons:
                    if rect.collidepoint(mx, my):
                        patient.med_given = med
                        show_message = [f"Selected: {med}"]
                        break

                # Admit button
                if admit_rect.collidepoint(mx, my):
                    patient.admitted = True
                    show_message = [f"{patient.name} has been admitted."]

                # Finish care
                if finish_rect.collidepoint(mx, my):
                    stars, reason = evaluate_patient(patient)

                    if stars == 0:
                        WIN.fill(WHITE)
                        y = 200
                        for line in reason.split("\n"):
                            draw_text(line, 100, y, RED)
                            y += 40
                        pygame.display.update()
                        pygame.time.delay(3500)
                        pygame.quit()
                        sys.exit()

                    total_rating.append(stars)

                    patients_treated += 1
                    if patients_treated >= 5:
                        day += 1
                        if day > 3:
                            WIN.fill(WHITE)
                            draw_text("You have proven this clinic deserves to stay open!", 120, 250, BLUE, BIG_FONT)
                            draw_text("Congratulations!", 350, 320, BLUE, BIG_FONT)
                            pygame.display.update()
                            pygame.time.delay(3500)
                            pygame.quit()
                            sys.exit()

                        # End of day screen
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

                    patient = generate_patient()
                    timer_start = pygame.time.get_ticks()
                    selected_med = None
                    show_message = None


if __name__ == "__main__":
    main()
