import json
import random
import urllib.request
from urllib.error import URLError, HTTPError

API_URL = "https://deckofcardsapi.com/api/deck/new/draw/?count=2"
FALLBACK_CARDS = [
    {"value": "7", "suit": "HEARTS"},
    {"value": "10", "suit": "SPADES"},
    {"value": "ACE", "suit": "CLUBS"},
    {"value": "4", "suit": "DIAMONDS"},
    {"value": "KING", "suit": "HEARTS"},
    {"value": "2", "suit": "SPADES"},
]


def get_value(card):
    value = str(card.get("value", "")).upper()
    face_cards = {"JACK": 11, "QUEEN": 12, "KING": 13, "ACE": 14}
    if value in face_cards:
        return face_cards[value]
    if value.isdigit():
        return int(value)
    raise ValueError(f"Unsupported card value: {card.get('value')}")


def evaluate_guess(first_card, second_card, guess):
    first_value = get_value(first_card)
    second_value = get_value(second_card)

    if second_value > first_value:
        return guess == "higher"
    if second_value < first_value:
        return guess == "lower"
    return "draw"


def draw_cards():
    try:
        with urllib.request.urlopen(API_URL, timeout=10) as response:
            payload = json.load(response)

        cards = payload.get("cards", [])
        if len(cards) < 2:
            raise ValueError("The API did not return enough cards")
        return cards[0], cards[1]
    except (URLError, HTTPError, TimeoutError, ValueError, json.JSONDecodeError):
        fallback_cards = list(FALLBACK_CARDS)
        random.shuffle(fallback_cards)
        return fallback_cards[0], fallback_cards[1]


def play_round():
    first_card, second_card = draw_cards()
    print(f"Current card: {first_card['value']} of {first_card['suit']}")
    guess = input("Will the next card be higher or lower? ").strip().lower()

    if guess not in {"higher", "lower"}:
        print("Please enter 'higher' or 'lower'.")
        return None

    result = evaluate_guess(first_card, second_card, guess)
    print(f"Next card: {second_card['value']} of {second_card['suit']}")

    if result == "draw":
        print("It's a draw!")
    elif result:
        print("You win!")
    else:
        print("You lose!")

    return result


def main():
    print("=" * 40)
    print("Welcome to Higher or Lower!")
    print("=" * 40)
    print("Rules:")
    print("- You see one card")
    print("- Guess if the next card will be higher or lower")
    print("- Score a point for each correct guess")
    print("- Type 'q' at any prompt to quit")
    print("=" * 40)

    score = 0
    while True:
        choice = input("Press enter to start a round or type 'q' to quit: ").strip().lower()
        if choice == "q":
            break

        try:
            round_result = play_round()
        except Exception as exc:
            print(f"Something went wrong: {exc}")
            break

        if round_result is None:
            continue
        if round_result == "draw":
            print("No score change.")
        elif round_result:
            score += 1
            print(f"Score: {score}")
        else:
            print(f"Score: {score}")

        again = input("Play again? (y/n): ").strip().lower()
        if again == "q":
            break
        if again != "y":
            break

    print("Thanks for playing!")


if __name__ == "__main__":
    main()
