function createSymbol(symbolName) {
    const symbol = document.createElement('div');
    symbol.classList.add('symbol');
    symbol.style.backgroundImage = `url(static/images/${symbolName.toLowerCase()}.png)`;
    return symbol;
}

function setReelSymbols(reel, symbols) {
    reel.innerHTML = '';
    symbols.forEach((symbol) => {
        const symbolElement = createSymbol(symbol);
        reel.appendChild(symbolElement);
    });
}

function animateSpin(reel) {
    const symbols = reel.querySelectorAll('.symbol');
    symbols.forEach(symbol => {
        symbol.style.animation = 'spin 0.5s linear infinite';
    });
}



function stopSpin(reel) {
    const symbol = reel.querySelector('.symbol');
    symbol.style.animation = '';
}

document.getElementById('play-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    const betSize = document.querySelector('input[name="bet_size"]').value;
    const spinDuration = 2000; // 2 seconds


    const response = await fetch('/play', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ bet_size: betSize })
    });

    const data = await response.json();
    const reelContainer = document.getElementById('reel-container');
    const reels = reelContainer.querySelectorAll('.reel');

    // Animate the reels with random symbols first
    reels.forEach((reel) => {
        const randomSymbols = [];
        for (let i = 0; i < 3; i++) {
            randomSymbols.push(data.all_symbols[Math.floor(Math.random() * data.all_symbols.length)]);
        }
        setReelSymbols(reel, randomSymbols);
        animateSpin(reel);
    });

    // After the spinning duration, stop the spin and set the actual result
    setTimeout(() => {
        data.symbols_array.forEach((symbol, index) => {
            stopSpin(reels[index]);
            setReelSymbols(reels[index], [symbol]);
        });

        document.getElementById('balance').innerText = data.balance;
        document.getElementById('result').innerText = `Payout: ${data.payout}`;
    }, spinDuration);
});


