import os
import gzip
import subprocess

# Pfade festlegen
DIR = r"C:\Users\Peter\Desktop\Gameboy"
ROM = os.path.join(DIR, "Pokemon - Emerald Version (USA, Europe).gba")
SAVE = os.path.join(DIR, "Pokemon - Emerald Version (USA, Europe)-01.sgm")
VBA = os.path.join(DIR, "visualboyadvance-m.exe")

def ultimate_admin_hack():
    print("🔓 Versuche Admin-Zugriff und Deep-Patch...")
    
    if not os.path.exists(SAVE):
        print("❌ Speicherdatei nicht gefunden!")
        return

    # 1. Datei einlesen und entpacken (Egal ob Gzip oder nicht)
    try:
        with gzip.open(SAVE, 'rb') as f:
            data = bytearray(f.read())
        compressed = True
    except:
        with open(SAVE, 'rb') as f:
            data = bytearray(f.read())
        compressed = False

    # 2. DEN SPEICHER FLUTEN (Das ist der eigentliche Hack)
    # Wir schreiben Simsala (ID 65) und Sonderbonbons (ID 68) 
    # einfach TAUSENDFACH in die Datei. Irgendeiner dieser Plätze MUSS 
    # der richtige für dein Team sein.
    
    # Kadabra (64) zu Simsala (65)
    data = data.replace(b'\x40\x00', b'\x41\x00')
    
    # Sonderbonbons (44 00) überall in den Beutel-Bereich hämmern
    for i in range(0x24000, 0x26000, 4):
        if i+4 < len(data):
            data[i:i+4] = b"\x44\x00\xE7\x03" # 999 Sonderbonbons

    # Boxen mit allen 386 Pokemon füllen (Level 50)
    for id in range(1, 387):
        pos = 0x1F000 + (id * 80)
        if pos + 80 < len(data):
            data[pos:pos+2] = id.to_bytes(2, 'little')
            data[pos+54] = 50 # Level 50
            data[pos+12:pos+20] = b"\x5E\x00\x55\x00\x3A\x00\x59\x00" # Attacken

    # 3. Datei zurückschreiben
    if compressed:
        with gzip.open(SAVE, 'wb') as f: f.write(data)
    else:
        with open(SAVE, 'wb') as f: f.write(data)

    # 4. ROM fixen (Damit die Entwicklung auch logisch erlaubt ist)
    with open(ROM, "rb+") as f:
        f.seek(0x325D1C)
        f.write(b"\x04\x00\x1E\x00\x41\x00")

    print("✅ System-Hack beendet. Starte Emulator...")
    subprocess.Popen([VBA, ROM])

if __name__ == "__main__":
    ultimate_admin_hack()