from flask import Flask, render_template, request
import json
from flask import jsonify
import os
import random
import numpy as np
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms

app = Flask(__name__)

# Probabilities and paytable
symbols = ['Cherry', 'Lemon', 'Orange', 'Plum', 'Bell', 'Bar', 'Seven']
probabilities = [0.3, 0.25, 0.16, 0.13, 0.1, 0.035, 0.025]

paytable = {('Cherry', 'Cherry', 'Cherry'): 4,
            ('Lemon', 'Lemon', 'Lemon'): 10,
            ('Orange', 'Orange', 'Orange'): 30,
            ('Plum', 'Plum', 'Plum'): 50,
            ('Bell', 'Bell', 'Bell'): 200,
            ('Bar', 'Bar', 'Bar'): 3000,
            ('Seven', 'Seven', 'Seven'): 10000}

# Define the number of reels and symbols on each reel
num_reels = 3
num_symbols = len(symbols)

def chacha_rng(key, nonce, counter, n_bytes):
    extended_nonce = nonce + counter.to_bytes(4, 'little')
    cipher = Cipher(algorithms.ChaCha20(key, extended_nonce), mode=None)
    encryptor = cipher.encryptor()
    return encryptor.update(b'\x00' * n_bytes)

def spin(bet_size):
    # ChaCha RNG to create random numbers
    key = os.urandom(32)
    nonce = os.urandom(12)
    counter = random.randint(0, 2**32 - 1)
    rng_values = chacha_rng(key, nonce, counter, num_reels * 4)

    # Convert RNG values to symbols
    rng_values_uint32 = np.frombuffer(rng_values, dtype=np.uint32)
    cumulative_probabilities = np.cumsum(probabilities)
    reels = np.searchsorted(cumulative_probabilities, rng_values_uint32 / 2**32)
    symbols_array = np.array(symbols)[reels]

    # Calculate the total payout
    symbol = tuple(symbols_array)
    if symbol in paytable:
        payout = paytable[symbol]
    else:
        payout = 0

    return payout * bet_size, symbols_array

@app.route('/')
def index():
    return render_template('index.html')

# Global user balance
user_balance = 1000

@app.route('/play', methods=['POST'])
def play():
    global user_balance
    bet_size = int(request.json['bet_size'])
    payout, symbols_array = spin(bet_size)
    user_balance -= bet_size  # Subtract the bet size from the balance
    user_balance += payout  # Add the payout to the balance

    return jsonify({'balance': user_balance, 'bet_size': bet_size, 'payout': payout, 'symbols_array': symbols_array.tolist(), 'all_symbols': symbols})

if __name__ == '__main__':
    app.run(debug=True)