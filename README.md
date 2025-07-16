# Tornado Simulator (Python)

🌪️ Experience the thrill of spawning and upgrading tornadoes to destroy towns and earn coins! This is the Python version of the Tornado Simulator game with upgradeable tornado levels, power-ups, promo codes, sound effects, and save/load functionality.

---

## Features

- Spawn tornadoes with varying power levels
- Upgrade tornado level (F1 to EF6)
- Upgrade power and coin multiplier
- Enter promo codes for free rewards
- Sound effects for success, failure, and milestone
- Save and load game progress automatically

---

## Requirements

- Python 3.7 or higher
- `pygame` library for audio playback
- `colorama` library for colored terminal output
- `numpy` library for math and rendering calculations

---

## Setup Instructions

1. **Clone or download this repository**

   ```bash
   git clone https://github.com/yourusername/tornado-simulator.git
   cd tornado-simulator
Create a virtual environment (optional but recommended)

python3 -m venv venv
source venv/bin/activate   # On Windows use: venv\Scripts\activate

Install required dependencies

pip install -r requirements.txt

If requirements.txt is not provided, manually install dependencies:

pip install pygame colorama numpy

Prepare audio files

Make sure the audio folder exists in the project directory.

Place all required .wav audio files inside audio/ folder:

success-tornado.wav

failed.wav

ef6-reached.wav

introsnd165.wav

funkytown.wav

Run the game

python tornado_simulator.py

How to Play
Follow on-screen prompts to spawn tornadoes, upgrade, and enter promo codes.

Your progress is saved automatically under the saves/ folder by username.

Promo codes can be obtained from the game’s creator or YouTube channel.

Troubleshooting
If audio fails to play, check if your system supports audio playback and that dependencies are installed.

For any missing module errors, verify your Python environment and installed packages.

If the save folder or audio folder does not exist, create them manually.

License
This project is open-source under the MIT License. Feel free to use and modify!

Contact
Created by LGMBrydan/YoBoiYeeter_.

Enjoy your tornado adventures! 🌪️
