from flask import Flask, jsonify, request, render_template
import uuid
from threading import Lock

from card_game import draw_cards, evaluate_guess, get_value

app = Flask(__name__)

# In-memory store for active rounds: token -> (first_card, second_card)
store = {}
store_lock = Lock()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/first', methods=['GET'])
def first_card():
    first, second = draw_cards()
    token = str(uuid.uuid4())
    with store_lock:
        store[token] = (first, second)
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

    return jsonify({
        'first': first,
        'second': second,
        'result': result
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
