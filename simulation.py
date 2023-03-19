import os
import random
import concurrent.futures
import numpy as np
import matplotlib.pyplot as plt
from tqdm.auto import tqdm
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms


def chacha_rng(key, nonce, counter, n_bytes):
    extended_nonce = nonce + counter.to_bytes(4, 'little')
    cipher = Cipher(algorithms.ChaCha20(key, extended_nonce), mode=None)
    encryptor = cipher.encryptor()
    return encryptor.update(b'\x00' * n_bytes)

# Probabilities and paytable
symbols = ['Cherry', 'Lemon', 'Orange', 'Plum', 'Bell', 'Bar', 'Seven']
probabilities = [0.3, 0.25, 0.16, 0.13, 0.1, 0.035, 0.025]

paytable = {('Cherry', 'Cherry', 'Cherry'): 4,
            ('Lemon', 'Lemon', 'Lemon'): 10,
            ('Orange', 'Orange', 'Orange'): 30,
            ('Plum', 'Plum', 'Plum'): 50,
            ('Bell', 'Bell', 'Bell'): 200,
            ('Bar', 'Bar', 'Bar'): 3000,
            ('Seven', 'Seven', 'Seven'): 8000}

# Define the number of reels and symbols on each reel
num_reels = 3
num_symbols = len(symbols)
num_threads = 8

def simulate_spin(bet_size, num_spins, thread_num):
    # ChaCha RNG to create random numbers
    key = os.urandom(32)
    nonce = os.urandom(12)
    counter = random.randint(0, 2**32 - 1)
    rng_values = chacha_rng(key, nonce, counter, num_spins * num_reels * 4)
    
    # Convert RNG values to symbols
    rng_values_uint32 = np.frombuffer(rng_values, dtype=np.uint32)
    cumulative_probabilities = np.cumsum(probabilities)
    reels = np.searchsorted(cumulative_probabilities, rng_values_uint32 / 2**32).reshape(num_spins, num_reels)
    symbols_array = np.array(symbols)[reels]

    # Calculate the total payout
    payout = np.zeros(num_spins)
    for i in range(num_spins):
        symbol = tuple(symbols_array[i, :])
        if symbol in paytable:
            payout[i] += paytable[symbol]

    return payout * bet_size

from tqdm.auto import tqdm

def calculate_rtp(num_spins, bet_size):
    # Calculate the return to player (RTP) over a given number of spins
    total_payout = 0
    spins_per_thread = num_spins // num_threads

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        future_payouts = {executor.submit(simulate_spin, bet_size, spins_per_thread, i): i for i in range(num_threads)}

        # Display progress bar
        progress_bar = tqdm(concurrent.futures.as_completed(future_payouts), total=num_threads, desc="Progress", unit="thread")

        for future in progress_bar:
            total_payout += future.result().sum()
            # Progress bar description
            progress_bar.set_description(f"Progress (Thread {future_payouts[future] + 1}/{num_threads})")

    total_bet = num_spins * bet_size
    rtp = total_payout / total_bet
    return rtp, future_payouts

# Still to work on the payout distribution plot over spins
# def create_payout_distribution_graph(payouts, num_spins):
#     plt.hist(payouts, bins=50)
#     plt.xlabel('Payout')
#     plt.ylabel('Frequency')
#     plt.title(f'Payout Distribution ({num_spins:,} spins)')
#     plt.show()

def create_running_rtp_graph(payouts, bet_size):
    running_total_payout = np.cumsum(payouts)
    running_total_bet = np.arange(1, len(payouts) + 1) * bet_size
    running_rtp = running_total_payout / running_total_bet

    plt.plot(running_rtp)
    plt.xlabel('Number of Spins')
    plt.ylabel('Running RTP')
    plt.title('Running RTP Over Time')
    plt.show()

def create_hits_per_combination_graph(payouts):
    hits_per_combination = {}
    
    for payout in payouts:
        for combination, value in paytable.items():
            if payout == value:
                if combination in hits_per_combination:
                    hits_per_combination[combination] += 1
                else:
                    hits_per_combination[combination] = 1

    combinations, hits = zip(*hits_per_combination.items())

    fig, ax = plt.subplots()
    bars = ax.barh(range(len(combinations)), hits)
    plt.yticks(range(len(combinations)), combinations)
    plt.xlabel('Hits')
    plt.ylabel('Winning Combination')
    plt.title('Hits per Winning Combination')

    # Hit counts as annotations
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax.annotate(f'{width}',
                    xy=(width, bar.get_y() + bar.get_height() / 2),
                    xytext=(3, 0),  # Horizontal offset
                    textcoords="offset points",
                    ha='left', va='center')

    plt.show()


# Simulation configuration (Number of spins and bet size)
num_spins = 10000000
bet_size = 1
rtp, future_payouts = calculate_rtp(num_spins, bet_size)

# Get the payouts
payouts = np.concatenate([future.result() for future in future_payouts])

print(f"RTP: {rtp:.2%}")

# Create the graphs
# create_payout_distribution_graph(payouts, num_spins)
create_running_rtp_graph(payouts, bet_size)
create_hits_per_combination_graph(payouts)
