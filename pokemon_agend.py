import os
import sys
import random
import cv2
import numpy as np
import time
import win32gui
import win32con
import mss
import gymnasium as gym
from gymnasium import spaces
from stable_baselines3 import PPO
import sqlite3
import requests
from datetime import datetime

# --- EMERGENCY NUMPY HACK ---
if np.__version__.startswith("2."):
    import numpy._core as _core
    sys.modules["numpy._core.numeric"] = _core.numeric
    sys.modules["numpy._core"] = _core

# --- CONFIG ---
NEW_MODEL_PATH = "omega_breeder_juggernaut"
DB_PATH = "pokemon_research.db"
DASHBOARD_URL = "http://localhost:8080/stats"
VK_MAP = {"UP": 0x57, "DOWN": 0x53, "LEFT": 0x41, "RIGHT": 0x44, "A": 0x4C, "B": 0x4B}

class BreederJuggernaut(gym.Env):
    def __init__(self):
        super().__init__()
        self.sct = mss.mss()
        self.hwnd = self._find_emulator_window("VisualBoyAdvance-M")
        
        # Action Space: 0:UP, 1:LEFT, 2:DOWN, 3:RIGHT, 4:A
        self.action_space = spaces.Discrete(5) 
        self.observation_space = spaces.Box(low=0, high=255, shape=(84, 84, 1), dtype=np.uint8)
        
        self._init_db()
        self.last_enemy_hp = 0
        self.last_obs = None
        self.stuck_counter = 0
        self.total_timesteps = 0
        self.battles_won = 0
        self.wall_collisions = 0
        self.start_time = time.time()

    def _init_db(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS training_stats 
                         (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                          timesteps INT, reward REAL, agent_id TEXT, 
                          battles_won INT, wall_collisions INT, 
                          fps REAL, timestamp DATETIME)''')
            conn.commit()
            conn.close()
        except Exception: pass

    def _find_emulator_window(self, substring):
        hwnds = []
        def callback(h, extra):
            if substring.lower() in win32gui.GetWindowText(h).lower(): extra.append(h)
        win32gui.EnumWindows(callback, hwnds)
        return hwnds[0] if hwnds else None

    def _get_screenshot(self):
        try:
            if not win32gui.IsWindow(self.hwnd):
                self.hwnd = self._find_emulator_window("VisualBoyAdvance-M")
            rect = win32gui.GetWindowRect(self.hwnd)
            if rect[0] < -30000: return np.zeros((84, 84, 1), dtype=np.uint8)
            monitor = {"top": rect[1]+32, "left": rect[0]+9, "width": 240, "height": 160}
            raw = np.array(self.sct.grab(monitor))
            self.current_frame = raw
            gray = cv2.cvtColor(raw, cv2.COLOR_BGRA2GRAY)
            self.roi_battle = gray[120:160, 10:110]
            self.roi_enemy_hp = gray[18:26, 15:85]
            return cv2.resize(gray, (84, 84)).reshape((84, 84, 1))
        except Exception: return np.zeros((84, 84, 1), dtype=np.uint8)

    def _update_dashboard_and_db(self, current_reward):
        fps = self.total_timesteps / (time.time() - self.start_time)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        payload = {
            "timesteps": self.total_timesteps, "reward": round(float(current_reward), 2),
            "battlesWon": self.battles_won, "wallCollisions": self.wall_collisions,
            "agentId": "Omega_Breeder_Gold_V6", "fps": round(fps, 2), "timestamp": timestamp
        }
        try: requests.post(DASHBOARD_URL, json=payload, timeout=0.1)
        except: pass
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("INSERT INTO training_stats (timesteps, reward, agent_id, battles_won, wall_collisions, fps, timestamp) VALUES (?,?,?,?,?,?,?)",
                         (payload["timesteps"], payload["reward"], payload["agentId"], payload["battles_won"], payload["wallCollisions"], payload["fps"], timestamp))
            conn.commit()
            conn.close()
        except: pass

    def step(self, action):
        self.total_timesteps += 1
        keys = ["UP", "LEFT", "DOWN", "RIGHT", "A"]
        key_name = keys[action]
        
        obs = self._get_screenshot()
        # Erkennt das Hauptmenü (Fight/Bag/Run/Poke)
        in_battle_menu = self.roi_battle.size > 0 and self.roi_battle.max() > 115
        reward = 0.0

        # --- PHYSIKALISCHE SPERRE ---
        if in_battle_menu:
            # Wenn das Hauptmenü offen ist, wird jede Aktion in 'A' umgewandelt.
            # Der Agent kann physikalisch NICHT auf 'Run' steuern.
            if key_name != "A":
                reward -= 100.0 # Bestrafung für den Versuch, das Menü zu verlassen
            
            key_name = "A" # Die Sperre: Im Hauptmenü wird IMMER A gesendet.
            
            curr_hp = np.count_nonzero(self.roi_enemy_hp > 100)
            if curr_hp < self.last_enemy_hp:
                reward += (self.last_enemy_hp - curr_hp) * 15000.0
                if curr_hp == 0: 
                    reward += 1000000.0 
                    self.battles_won += 1
            self.last_enemy_hp = curr_hp
        else:
            # Im Attacken-Menü oder auf der Map: Freie Steuerung
            self.last_enemy_hp = 0
            # Gras-Sucht (Breeder Exploration)
            hsv = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2HSV)
            if np.sum(cv2.inRange(hsv, (35, 40, 40), (85, 255, 255))) > 4000:
                reward += 100.0

        # Stuck Detection
        if self.last_obs is not None and np.mean(cv2.absdiff(obs, self.last_obs)) < 0.2:
            self.stuck_counter += 1
            self.wall_collisions += 1
        else: self.stuck_counter = 0

        if self.stuck_counter > 20 and not in_battle_menu:
            key_name = random.choice(["UP", "LEFT", "DOWN", "RIGHT"])
            self.stuck_counter = 0

        if self.total_timesteps % 100 == 0:
            self._update_dashboard_and_db(reward)

        # --- EINGABE SENDEN ---
        win32gui.PostMessage(self.hwnd, win32con.WM_KEYDOWN, VK_MAP[key_name], 0)
        time.sleep(0.05)
        win32gui.PostMessage(self.hwnd, win32con.WM_KEYUP, VK_MAP[key_name], 0)
        
        # Kleiner A-Spam im Kampf um Textboxen zu überspringen
        if in_battle_menu:
            win32gui.PostMessage(self.hwnd, win32con.WM_KEYDOWN, VK_MAP["A"], 0)
            win32gui.PostMessage(self.hwnd, win32con.WM_KEYUP, VK_MAP["A"], 0)

        self.last_obs = obs
        return obs, reward, False, False, {}

    def reset(self, seed=None, options=None):
        return self._get_screenshot(), {}

def train():
    env = BreederJuggernaut()
    print(f"🚀 OMEGA-BREEDER GOLD V6: Wegrennen physikalisch gesperrt!")
    model = PPO("CnnPolicy", env, verbose=1, device="cpu", ent_coef=0.07, learning_rate=0.0003)
    model.learn(total_timesteps=100_000_000)

if __name__ == "__main__":
    train()