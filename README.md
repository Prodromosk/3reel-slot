# Simple Guide to Using and Customizing simulation.py
This script simulates a slot machine using the ChaCha20 random number generator. It calculates the Return to Player (RTP) and generates graphs to visualize the results.

## How to Use
Ensure you have the required packages installed:

numpy
matplotlib
tqdm
cryptography
You can install them using pip:

```bash
pip install numpy matplotlib tqdm cryptography
```
OR
```bash
pip install requirements.txt
```
## Run the script using Python:

```bash
python simulation.py
```
Observe the results, including the calculated RTP and the generated graphs.

## How to Customize
1. Modify the symbols and their probabilities
You can customize the slot machine by modifying the symbols and probabilities variables:

```python
symbols = ['Cherry', 'Lemon', 'Orange', 'Plum', 'Bell', 'Bar', 'Seven']
probabilities = [0.3, 0.25, 0.16, 0.13, 0.1, 0.035, 0.025]
```
symbols is a list of strings representing the slot machine symbols.
probabilities is a list of floats representing the probability of each symbol appearing on a reel.
Make sure the probabilities add up to 1.

## 2. Modify the paytable
You can customize the payouts by modifying the paytable variable:

```python
paytable = {('Cherry', 'Cherry', 'Cherry'): 4,
            ('Lemon', 'Lemon', 'Lemon'): 10,
            ('Orange', 'Orange', 'Orange'): 30,
            ('Plum', 'Plum', 'Plum'): 50,
            ('Bell', 'Bell', 'Bell'): 200,
            ('Bar', 'Bar', 'Bar'): 3000,
            ('Seven', 'Seven', 'Seven'): 8000}
```
paytable is a dictionary where the keys are tuples representing winning combinations, and the values are the payouts for those combinations.

## 3. Modify the number of spins and bet size
You can change the number of spins and the bet size by modifying the num_spins and bet_size variables:

```python
num_spins = 10000000
bet_size = 1
```
- num_spins is the total number of spins in the simulation.
- bet_size is the size of the bet for each spin.
## 4. Modify the number of threads
You can change the number of threads used in the simulation by modifying the num_threads variable:

```python
num_threads = 8
```
num_threads is the number of threads used to speed up the simulation. Set this value based on the number of cores available on your system.

# Simple Guide to initiate a dev server to play the game using flask
This Flask web application simulates a slot machine using the ChaCha20 random number generator. Users can place bets and spin the reels, while the app calculates the payouts and keeps track of the user's balance.

How to Use
Ensure you have the required packages installed:

Flask
You can install it using pip:

```bash
pip install numpy flask cryptography
```
OR
```bash
pip install requirements.txt
```
Run the script using Python:

```bash
python app.py
```
Open a web browser and navigate to http://localhost:5000/ to access the slot machine.

Place bets and spin the reels to play the game.
