import unittest

from app import app, store, store_lock


class AppApiTests(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.client = app.test_client()
        with store_lock:
            store.clear()

    def test_guess_response_returns_next_token_for_next_round(self):
        first_response = self.client.get('/first')
        self.assertEqual(first_response.status_code, 200)
        first_payload = first_response.get_json()
        token = first_payload['token']

        guess_response = self.client.post('/guess', json={'token': token, 'guess': 'higher'})
        self.assertEqual(guess_response.status_code, 200)
        guess_payload = guess_response.get_json()

        self.assertIn('first', guess_payload)
        self.assertIn('second', guess_payload)
        self.assertIn('result', guess_payload)
        self.assertIn('next_token', guess_payload)
        self.assertIsInstance(guess_payload['next_token'], str)

        next_round_response = self.client.post('/guess', json={
            'token': guess_payload['next_token'],
            'guess': 'higher'
        })
        self.assertEqual(next_round_response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
