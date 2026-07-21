import unittest
from unittest.mock import patch
from urllib.error import URLError

from card_game import draw_cards, evaluate_guess, get_value


class GameLogicTests(unittest.TestCase):
    def test_get_value_maps_face_cards(self):
        self.assertEqual(get_value({"value": "KING", "suit": "SPADES"}), 13)
        self.assertEqual(get_value({"value": "ACE", "suit": "HEARTS"}), 14)

    def test_evaluate_guess_detects_higher(self):
        first_card = {"value": "5", "suit": "CLUBS"}
        second_card = {"value": "9", "suit": "DIAMONDS"}
        self.assertEqual(evaluate_guess(first_card, second_card, "higher"), "correct")
        self.assertEqual(evaluate_guess(first_card, second_card, "lower"), "incorrect")

    def test_evaluate_guess_detects_lower(self):
        first_card = {"value": "10", "suit": "SPADES"}
        second_card = {"value": "4", "suit": "HEARTS"}
        self.assertEqual(evaluate_guess(first_card, second_card, "lower"), "correct")
        self.assertEqual(evaluate_guess(first_card, second_card, "higher"), "incorrect")

    def test_evaluate_guess_treats_tie_as_draw(self):
        first_card = {"value": "7", "suit": "CLUBS"}
        second_card = {"value": "7", "suit": "DIAMONDS"}
        self.assertEqual(evaluate_guess(first_card, second_card, "higher"), "draw")

    def test_draw_cards_falls_back_when_api_fails(self):
        with patch("card_game.urllib.request.urlopen", side_effect=URLError("offline")):
            first_card, second_card = draw_cards()

        self.assertIn(first_card["value"], {card["value"] for card in [
            {"value": "7", "suit": "HEARTS"},
            {"value": "10", "suit": "SPADES"},
            {"value": "ACE", "suit": "CLUBS"},
            {"value": "4", "suit": "DIAMONDS"},
            {"value": "KING", "suit": "HEARTS"},
            {"value": "2", "suit": "SPADES"},
        ]})
        self.assertIn(second_card["value"], {card["value"] for card in [
            {"value": "7", "suit": "HEARTS"},
            {"value": "10", "suit": "SPADES"},
            {"value": "ACE", "suit": "CLUBS"},
            {"value": "4", "suit": "DIAMONDS"},
            {"value": "KING", "suit": "HEARTS"},
            {"value": "2", "suit": "SPADES"},
        ]})


if __name__ == "__main__":
    unittest.main()
