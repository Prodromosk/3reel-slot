from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend
import os

class SlotGame:
    def __init__(self, reels, rows, symbols, premium_symbols, wild_symbol, bonus_symbol, rtp):
        self.reels = reels
        self.rows = rows
        self.symbols = symbols
        self.premium_symbols = premium_symbols
        self.wild_symbol = wild_symbol
        self.bonus_symbol = bonus_symbol
        self.rtp = rtp
        self.paytable = self.generate_paytable()
        self.chacha20 = self.init_chacha20()
        self.paylines = self.generate_paylines()

    def init_chacha20(self):
        private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
        peer_public_key = private_key.public_key()
        peer_public_key_pem = peer_public_key.public_bytes(encoding=serialization.Encoding.PEM,
                                                        format=serialization.PublicFormat.SubjectPublicKeyInfo)
        shared_key = private_key.exchange(ec.ECDH(), serialization.load_pem_public_key(peer_public_key_pem, default_backend()))
        nonce = os.urandom(16)
        return Cipher(algorithms.ChaCha20(shared_key, nonce), mode=None, backend=default_backend()).encryptor()

    def chacha_random(self, min_value, max_value):
        random_bytes = self.chacha20.update(b'\x00\x00\x00\x00')
        random_int = int.from_bytes(random_bytes, byteorder='little')
        return min_value + (random_int % (max_value - min_value + 1))

    def generate_paytable(self):
        paytable = {}
        for i, symbol in enumerate(self.symbols + self.premium_symbols):
            paytable[symbol] = (i + 1) * 10

        for i, symbol in enumerate(self.premium_symbols):
            paytable[symbol] = (i + 1) * 50

        return paytable

    def generate_paylines(self):
        paylines = [
            [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0)],
            [(0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1)],
            [(0, 2), (1, 2), (2, 2), (3, 2), (4, 2), (5, 2)],
            [(0, 3), (1, 3), (2, 3), (3, 3), (4, 3), (5, 3)],
            [(0, 4), (1, 4), (2, 4), (3, 4), (4, 4), (5, 4)],
            [(0, 0), (1, 1), (2, 2), (3, 2), (4, 1), (5, 0)],
            [(0, 4), (1, 3), (2, 2), (3, 2), (4, 3), (5, 4)],
            [(0, 0), (1, 0), (2, 1), (3, 1), (4, 0), (5, 0)],
            [(0, 4), (1, 4), (2, 3), (3, 3), (4, 4), (5, 4)],
            [(0, 2), (1, 2), (2, 1), (3, 1), (4, 2), (5, 2)]
        ]
        return paylines

    def spin(self):
        all_symbols = self.symbols + self.premium_symbols + [self.wild_symbol, self.bonus_symbol]
        grid = [[all_symbols[self.chacha_random(0, len(all_symbols) - 1)] for _ in range(self.rows)] for _ in range(self.reels)]
        return grid


    def check_win(self, grid):
        win_amount = 0
        bonus_triggered = False
        bonus_count = sum(row.count(self.bonus_symbol) for row in grid)

        if bonus_count >= 3:
            bonus_triggered = True

        for payline in self.paylines:
            symbols_on_line = [grid[r][c] for r, c in payline]

            # Wild symbol substitution
            if self.wild_symbol in symbols_on_line:
                non_wild_symbols = [symbol for symbol in symbols_on_line if symbol != self.wild_symbol]
                if len(set(non_wild_symbols)) == 1:
                    win_amount += self.paytable[non_wild_symbols[0]] * symbols_on_line.count(self.wild_symbol)

            # Regular wins
            elif len(set(symbols_on_line)) == 1:
                win_amount += self.paytable[symbols_on_line[0]]

        if bonus_triggered:
            return "BONUS"

        return win_amount if win_amount > 0 else 0



    def play(self, bet_amount, num_spins):
        total_win = 0
        for _ in range(num_spins):
            grid = self.spin()
            win_amount = self.check_win(grid)
            total_win += win_amount
        return bet_amount * num_spins * self.rtp - total_win

symbols = ["A", "K", "Q", "J", "10", "9"]
premium_symbols = ["P1", "P2", "P3"]
wild_symbol = "W"
bonus_symbol = "B"

reels = 6
rows = 5
rtp = 0.964

game = SlotGame(reels, rows, symbols, premium_symbols, wild_symbol, bonus_symbol, rtp)

def bonus_feature():
    # Implement your bonus feature logic here
    # This is just a simple example, returning a random win amount
    return game.chacha_random(100, 500)

bet_amount = 1
num_spins = 100
total_win = 0

for spin in range(1, num_spins + 1):
    grid = game.spin()
    win_amount = game.check_win(grid)

    if win_amount == "BONUS":
        bonus_win = bonus_feature()
        total_win += bonus_win
        print(f"Spin {spin}: Bonus triggered! Win amount: {bonus_win}")
    else:
        total_win += win_amount
        print(f"Spin {spin}: Win amount: {win_amount}")

    # Print the grid representation
    for row in range(rows):
        print(" ".join(grid[col][row] for col in range(reels)))
    print("\n")

result = bet_amount * num_spins * game.rtp - total_win
print(f"Result after {num_spins} spins: {result:.2f}")
           
