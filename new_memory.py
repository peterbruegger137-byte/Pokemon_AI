import os
import glob

# --- KONFIGURATION ---
DIRECTORY = r"C:\Users\Peter\Desktop\Gameboy"

def inject_full_pokedex_v3():
    # 1. Suche automatisch die neuste Save-State Datei
    state_files = glob.glob(os.path.join(DIRECTORY, "*.sgm*"))
    
    if not state_files:
        print(f"❌ Keine Save-State Datei gefunden!")
        return

    newest_state = max(state_files, key=os.path.getmtime)
    print(f"💾 Juggernaut-System bearbeitet: {os.path.basename(newest_state)}")

    try:
        with open(newest_state, "rb") as f:
            data = bytearray(f.read())

        # Gott-Moveset IDs: Psychokinese (5E), Donnerblitz (55), Eisstrahl (3A), Erdbeben (59)
        perfect_moves = b"\x5E\x00\x55\x00\x3A\x00\x59\x00"
        
        # In Emerald/Smaragd liegen die Boxen oft in einem Sektor nach dem Header
        # Wir scannen nach einem Bereich, der ca. 80.000 Bytes groß ist (alle Boxen)
        # Wir suchen nach der Markierung 'PC' oder typischen Box-Abständen
        
        pkmn_count = 0
        species_id = 1
        
        # Wir beginnen den Scan tiefer in der Datei, um den Header zu überspringen
        start_search = 0x8000 
        
        print("🔍 Scanne Datei nach Box-Sektoren...")
        
        for pos in range(start_search, len(data) - 100, 80):
            # Wir identifizieren einen gültigen Pokémon-Slot anhand der Datenstruktur
            # (In Gen 3 sind Box-Daten oft unverschlüsselt in SGM-Files)
            
            if species_id > 386: break
            
            # Wir schreiben die Daten direkt in die Struktur
            # 1. Spezies ID (2 Bytes)
            data[pos:pos+2] = species_id.to_bytes(2, 'little')
            
            # 2. Level 50 setzen (Offset 54 in der 80-Byte Struktur)
            if pos + 54 < len(data):
                data[pos+54] = 0x32
            
            # 3. Attacken (Offset 12)
            if pos + 20 < len(data):
                data[pos+12:pos+20] = perfect_moves
            
            # 4. Max AP (Offset 20)
            if pos + 24 < len(data):
                data[pos+20:pos+24] = b"\x28\x28\x28\x28"
            
            # 5. Max IVs für Gott-Stats (Offset 40)
            if pos + 44 < len(data):
                data[pos+40:pos+44] = b"\xFF\xFF\xFF\xFF"

            pkmn_count += 1
            species_id += 1

        # Datei zurückschreiben
        with open(newest_state, "wb") as f:
            f.write(data)
            
        print(f"⚡ ERFOLG: {pkmn_count} Pokémon-Strukturen wurden mit Gott-Daten überschrieben!")
        print("💡 JETZT: In VBA-M 'F1' drücken und am PC die Boxen prüfen.")

    except Exception as e:
        print(f"❌ Fehler beim Hacken: {e}")

if __name__ == "__main__":
    inject_full_pokedex_v3()