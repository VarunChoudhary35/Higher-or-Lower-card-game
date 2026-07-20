from flask import Flask, jsonify, request, render_template
import logging
import uuid
from threading import Lock

from card_game import draw_cards, evaluate_guess, get_value

app = Flask(__name__)

# basic logging so Railway runtime logs show startup
logging.basicConfig(level=logging.INFO)
app.logger.info("app module imported")

# In-memory store for active rounds: token -> (first_card, second_card)
store = {}
store_lock = Lock()

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/health', methods=['GET'])
def health():
    # simple health check for platform probes
    return jsonify({'status': 'ok'})

def _create_round():
    first, second = draw_cards()
    token = str(uuid.uuid4())
    with store_lock:
        store[token] = (first, second)
    return token, first, second


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

    first, second = pair
    result = evaluate_guess(first, second, guess)
    next_token, next_first, _ = _create_round()

    return jsonify({
        'first': first,
        'second': second,
        'result': result,
        'next_token': next_token,
        'next_first': next_first
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
