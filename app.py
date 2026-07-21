from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import logging
import uuid
from threading import Lock

from card_game import draw_cards, evaluate_guess

app = Flask(__name__)
CORS(app)

# basic logging so Railway runtime logs show startup
logging.basicConfig(level=logging.INFO)
app.logger.info("app module imported")

# In-memory store for active rounds: token -> (current_card, next_card)
store = {}
store_lock = Lock()

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/health', methods=['GET'])
def health():
    # simple health check for platform probes
    return jsonify({'status': 'ok'})

def _create_round(current_card=None):
    first, second = draw_cards()
    token = str(uuid.uuid4())
    if current_card is None:
        current_card = first
    with store_lock:
        store[token] = (current_card, second)
    return token, current_card, second


@app.route('/first', methods=['GET'])
def first_card():
    token, first, _ = _create_round()
    return jsonify({
        'token': token,
        'first': first
    })


@app.route('/guess', methods=['POST'])
def guess():
    data = request.get_json() or {}
    token = data.get('token')
    guess = (data.get('guess') or '').lower()
    if not token or guess not in {'higher', 'lower'}:
        return jsonify({'error': 'missing token or invalid guess'}), 400

    with store_lock:
        pair = store.pop(token, None)
    if not pair:
        return jsonify({'error': 'invalid or expired token'}), 400

    current_card, next_card = pair
    result = evaluate_guess(current_card, next_card, guess)

    next_token, next_current_card, next_next_card = _create_round(current_card=next_card)

    return jsonify({
        'first': current_card,
        'second': next_card,
        'result': result,
        'next_token': next_token,
        'next_card': next_card
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
