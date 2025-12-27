import pydirectinput
import win32gui
import time

# Konfiguration basierend auf deinem Screenshot
WINDOW_TITLE = "VisualBoyAdvance"
TEST_KEYS = ["w", "a", "s", "d", "l", "k", "enter"]

def test_connection():
    hwnd = win32gui.FindWindow(None, WINDOW_TITLE)
    if not hwnd:
        print(f"❌ FEHLER: Fenster '{WINDOW_TITLE}' nicht gefunden!")
        print("Stelle sicher, dass der Emulator offen ist und der Titel exakt stimmt.")
        return

    print(f"✅ Emulator gefunden (HWND: {hwnd}).")
    print("Bringe Fenster in den Fokus...")
    
    try:
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(1)
    except Exception as e:
        print(f"⚠️ Fokus-Fehler: {e}. Starte das Terminal als ADMIN!")

    print("Starte Tastatur-Test in 3 Sekunden...")
    time.sleep(3)

    for key in TEST_KEYS:
        print(f"Sende Taste: {key}")
        pydirectinput.press(key)
        time.sleep(0.5)

    print("\nTest abgeschlossen. Hat sich die Spielfigur bewegt?")

if __name__ == "__main__":
    test_connection()