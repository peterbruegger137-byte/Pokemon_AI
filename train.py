import pymem
import pymem.process

def memory_god_mode_injector():
    try:
        # 1. Verbindung zum Emulator
        pm = pymem.Pymem("visualboyadvance-m.exe")
        print("✅ Verbindung zu VisualBoyAdvance-M hergestellt.")

        # 2. Suche nach der Signatur deines Manectric
        # Roar (2E) und Quick Attack (62) sind aktuell im RAM.
        # Wir suchen nach der Byte-Folge: 2E 00 62 00
        pattern = b"\x2E\x00\x62\x00"
        address = pm.pattern_scan_all(pattern)

        if address:
            print(f"🎯 Echtzeit-Adresse im Windows-RAM gefunden: {hex(address)}")
            
            # --- MANECTRIC (Slot 1 im Team) ---
            # Donner (57), Donnerblitz (55), Blattschnitt (CE), Knirscher (F2)
            pm.write_short(address, 0x0057)      # Slot 1
            pm.write_short(address + 2, 0x0055)  # Slot 2
            pm.write_short(address + 4, 0x00CE)  # Slot 3
            pm.write_short(address + 6, 0x00F2)  # Slot 4

            # --- REDY (Slot 2 im Team - liegt 100 Bytes weiter) ---
            redy_addr = address + 0x64
            pm.write_short(redy_addr, 0x00CE)     # Slot 1: Blattschnitt
            pm.write_short(redy_addr + 2, 0x004C) # Slot 2: Solarstrahl

            # --- KADABRA ZU SIMSALA (Slot 3 im Team) ---
            # Wir ändern die Spezies-ID von 41 (Kadabra) zu 42 (Simsala)
            # Die Spezies-ID liegt bei Smaragd an einem Offset zur Attacke
            # Wir nutzen hier den Slot 3 (200 Bytes nach Slot 1)
            pm.write_short(address + 0xC8, 0x0042)

            print("⚡ GOD-MODE & ENTWICKLUNG ERFOLGREICH INJIZIERT!")
            print("💡 Öffne jetzt den Bericht im Spiel, um die Änderungen zu sehen.")
        else:
            print("❌ Signatur nicht gefunden!")
            print("Tipp: Stelle sicher, dass Manectric an Pos. 1 ist und Roar/Quick Attack hat.")

    except Exception as e:
        print(f"❌ Fehler: {e}")

if __name__ == "__main__":
    memory_god_mode_injector()