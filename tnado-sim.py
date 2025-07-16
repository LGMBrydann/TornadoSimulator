import random
import time
import numpy as np
import sys
import threading
import json
import os
import pygame
from colorama import Fore, Style, init

init(autoreset=True)  # For colored terminal output

# === Donut Constants ===
screen_size = 40
theta_spacing = 0.07
phi_spacing = 0.02
illumination = np.fromiter(".,-~:;=!*#$@", dtype="<U1")

A = 1
B = 1
R1 = 1
R2 = 2
K2 = 5
K1 = screen_size * K2 * 3 / (8 * (R1 + R2))

SAVE_FOLDER = "saves"
AUDIO_FOLDER = "audio"

if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)

def render_frame(A: float, B: float) -> np.ndarray:
    cos_A = np.cos(A)
    sin_A = np.sin(A)
    cos_B = np.cos(B)
    sin_B = np.sin(B)

    output = np.full((screen_size, screen_size), " ")
    zbuffer = np.zeros((screen_size, screen_size))

    cos_phi = np.cos(phi := np.arange(0, 2 * np.pi, phi_spacing))
    sin_phi = np.sin(phi)
    cos_theta = np.cos(theta := np.arange(0, 2 * np.pi, theta_spacing))
    sin_theta = np.sin(theta)
    circle_x = R2 + R1 * cos_theta
    circle_y = R1 * sin_theta

    x = (np.outer(cos_B * cos_phi + sin_A * sin_B * sin_phi, circle_x) - circle_y * cos_A * sin_B).T
    y = (np.outer(sin_B * cos_phi - sin_A * cos_B * sin_phi, circle_x) + circle_y * cos_A * cos_B).T
    z = ((K2 + cos_A * np.outer(sin_phi, circle_x)) + circle_y * sin_A).T
    ooz = np.reciprocal(z)
    xp = (screen_size / 2 + K1 * ooz * x).astype(int)
    yp = (screen_size / 2 - K1 * ooz * y).astype(int)
    L1 = (((np.outer(cos_phi, cos_theta) * sin_B) - cos_A * np.outer(sin_phi, cos_theta)) - sin_A * sin_theta)
    L2 = cos_B * (cos_A * sin_theta - np.outer(sin_phi, cos_theta * sin_A))
    L = np.around(((L1 + L2) * 8)).astype(int).T
    mask_L = L >= 0
    chars = illumination[L]

    for i in range(90):
        mask = mask_L[i] & (ooz[i] > zbuffer[xp[i], yp[i]])
        zbuffer[xp[i], yp[i]] = np.where(mask, ooz[i], zbuffer[xp[i], yp[i]])
        output[xp[i], yp[i]] = np.where(mask, chars[i], output[xp[i], yp[i]])

    return output

def pprint(array: np.ndarray) -> None:
    print(*[" ".join(row) for row in array], sep="\n")

def play_music(filename):
    path = os.path.join(AUDIO_FOLDER, filename)
    if os.path.exists(path):
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()
        except Exception as e:
            print(f"\n⚠️ Error playing sound: {e}")
    else:
        print(f"\n⚠️ Audio file not found: {path}")

def play_sound_effect(filename):
    path = os.path.join(AUDIO_FOLDER, filename)
    if os.path.exists(path):
        try:
            pygame.mixer.init()
            sound = pygame.mixer.Sound(path)
            sound.play()
        except Exception as e:
            print(f"\n⚠️ Error playing sound: {e}")

def loading_screen():
    duration = 44
    bar_length = 30
    print("\n🌪️ Loading Tornado Simulator... Funkytown is playing! 🎶\n")
    music_thread = threading.Thread(target=play_music, args=("funkytown.mp3",), daemon=True)
    music_thread.start()
    start_time = time.time()
    while True:
        elapsed = time.time() - start_time
        if elapsed > duration:
            break
        progress = elapsed / duration
        filled_length = int(bar_length * progress)
        bar = "█" * filled_length + "-" * (bar_length - filled_length)
        print(f"\rLoading: |{bar}| {int(progress * 100)}%", end="", flush=True)
        time.sleep(0.1)
    print("\rLoading: |" + "█" * bar_length + "| 100%")
    print("\n✅ Done loading! Starting the simulator...\n")

levels = {
    1: {"name": "F1", "damage": 10, "cost": 0},
    2: {"name": "F2", "damage": 25, "cost": 50},
    3: {"name": "F3", "damage": 50, "cost": 100},
    4: {"name": "F4", "damage": 100, "cost": 200},
    5: {"name": "F5", "damage": 200, "cost": 500},
    6: {"name": "EF6", "damage": 400, "cost": 1000}
}

promo_codes = {
    "FIRSTRELEASE2025": {"power_upgrade": 1},
    "LRACE2": {"coins": 5000},
    "500YTSUBS": {"coins": 10000},
    "YT2025.": {"coins": 3000},
    "FUNKAY88": {"coins": 999999},
}

def visual_effect(msg, color=Fore.CYAN):
    print(color + "=" * 50)
    print(color + msg.center(50))
    print(color + "=" * 50)

def save_game(username, data):
    with open(os.path.join(SAVE_FOLDER, f"{username}.json"), "w") as f:
        json.dump(data, f)

def load_game(username):
    path = os.path.join(SAVE_FOLDER, f"{username}.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return None

def spawn_tornado(state):
    base_power = levels[state["tornado_level"]]["damage"]
    total_power = base_power + (state["power_upgrade_level"] * 20)
    town_hp = random.randint(50, 300)
    print(f"\n🌪️ You spawned a {levels[state['tornado_level']]['name']} Tornado!")
    print(f"🔋 Power: {total_power} vs 🏘️ Town HP: {town_hp}")
    time.sleep(1)
    if total_power >= town_hp:
        reward = (town_hp + random.randint(20, 50)) * state["coin_multiplier"]
        state["coins"] += reward
        state["towns_destroyed"] += 1
        play_sound_effect("success-tornado.wav")
        visual_effect(f"💥 Town Destroyed! Earned {reward} coins!", Fore.YELLOW)
    else:
        print("❌ Town Survived. Not strong enough.")
        play_sound_effect("failed.wav")

def upgrade_tornado(state):
    if state["tornado_level"] >= 6:
        print("🌀 Max tornado level reached: EF6!")
        play_sound_effect("failed.wav")
        return
    next_level = state["tornado_level"] + 1
    cost = levels[next_level]["cost"]
    if state["coins"] >= cost:
        state["coins"] -= cost
        state["tornado_level"] = next_level
        visual_effect(f"⬆️ Upgraded to {levels[state['tornado_level']]['name']}!", Fore.GREEN)
        # Play EF6 reached sound
        if state["tornado_level"] == 6:
            play_sound_effect("ef6-reached.wav")
    else:
        print(f"❌ Not enough coins. Need {cost}, you have {state['coins']}.")
        play_sound_effect("failed.wav")

def upgrade_power(state):
    cost = 100 + state["power_upgrade_level"] * 100
    if state["coins"] >= cost:
        state["coins"] -= cost
        state["power_upgrade_level"] += 1
        visual_effect(f"🧪 Power upgraded! +{state['power_upgrade_level'] * 20} bonus damage.", Fore.MAGENTA)
    else:
        print(f"❌ Not enough coins for power upgrade. Need {cost}.")
        play_sound_effect("failed.wav")

def upgrade_multiplier(state):
    cost = 200 + (state["coin_multiplier"] - 1) * 200
    if state["coins"] >= cost:
        state["coins"] -= cost
        state["coin_multiplier"] += 1
        visual_effect(f"💰 Multiplier increased to x{state['coin_multiplier']}!", Fore.BLUE)
    else:
        print(f"❌ Not enough coins for multiplier upgrade. Need {cost}.")
        play_sound_effect("failed.wav")

def promo_code_menu(state):
    print("\n=== 🎟️ Promo Code Menu ===")
    print("You can get free coins or upgrades by entering promo codes that I will share on my YouTube channel!")
    print("Type 'back' to return to main menu.")
    while True:
        code = input("Enter promo code: ").strip().upper()
        if code == "BACK":
            break
        elif code in promo_codes:
            reward = promo_codes[code]
            if "coins" in reward:
                state["coins"] += reward["coins"]
                play_sound_effect("success-tornado.wav")
                visual_effect(f"🎉 Promo accepted! +{reward['coins']} coins!", Fore.YELLOW)
            if "power_upgrade" in reward:
                state["power_upgrade_level"] += reward["power_upgrade"]
                visual_effect(f"🎉 Promo accepted! +{reward['power_upgrade']} power upgrade!", Fore.MAGENTA)
            del promo_codes[code]
            break
        else:
            print("❌ Invalid or already used promo code.")
            play_sound_effect("failed.wav")

def main():
    print("🌪️ Welcome to Tornado Simulator! 🌪️")
    username = input("Enter your username: ").strip()
    if not username:
        username = "Player"
    state = load_game(username)
    if state is None:
        print("👋 Hello, new player! You get 500 free coins to start.")
        state = {
            "coins": 500,
            "tornado_level": 1,
            "towns_destroyed": 0,
            "power_upgrade_level": 0,
            "coin_multiplier": 1,
            "username": username
        }
    loading_screen()
    print(f"👋 Welcome, {username}!")
    play_music("introsnd165.mp3")
    while True:
        print(f"\n=== 🌪️ TORNADO SIMULATOR: EF6 MODE ===")
        print(f"Player: {state['username']}")
        print(f"🌪️ Tornado: {levels[state['tornado_level']]['name']} | 💥 Power Bonus: +{state['power_upgrade_level'] * 20} | x{state['coin_multiplier']} Coins")
        print(f"💰 Coins: {state['coins']} | 🏘️ Towns Destroyed: {state['towns_destroyed']}")
        print("\nActions:")
        print("1. Spawn Tornado")
        print("2. Upgrade Tornado (F1 → EF6)")
        print("3. Upgrade Power (More Damage)")
        print("4. Upgrade Coin Multiplier")
        print("5. Enter Promo Code")
        print("6. Exit")
        choice = input("Choose an option (1-6): ").strip()
        if choice == '1':
            spawn_tornado(state)
            save_game(username, state)
        elif choice == '2':
            upgrade_tornado(state)
            save_game(username, state)
        elif choice == '3':
            upgrade_power(state)
            save_game(username, state)
        elif choice == '4':
            upgrade_multiplier(state)
            save_game(username, state)
        elif choice == '5':
            promo_code_menu(state)
            save_game(username, state)
        elif choice == '6':
            print("👋 Thanks for playing EF6 Tornado Simulator!")
            save_game(username, state)
            break
        else:
            print("❓ Invalid choice.")
            play_sound_effect("failed.wav")

if __name__ == "__main__":
    main()
