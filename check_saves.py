import os
import glob
from datetime import datetime

def check_save_states():
    # Der Pfad zu deinem Emulator-Ordner
    save_path = r"C:\Users\Peter\Desktop\Gameboy"
    # Endungen für VBA-M Save States
    state_files = glob.glob(os.path.join(save_path, "*.sg*")) 

    print("##################################################")
    print("🔍 MASTERCONTROLLER: SAVE-STATE ANALYSE")
    print("##################################################\n")

    if not state_files:
        print("❌ Keine Save-State Dateien gefunden (.sgm oder .sg1-10).")
        return

    # Sortieren nach Datum (neueste zuerst)
    state_files.sort(key=os.path.getmtime, reverse=True)

    print(f"Gefundene States: {len(state_files)}\n")
    print(f"{'Dateiname':<40} | {'Erstellt am':<20} | {'Größe'}")
    print("-" * 80)

    for file in state_files:
        stats = os.stat(file)
        dt = datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        size = f"{stats.st_size / 1024:.1f} KB"
        name = os.path.basename(file)
        
        indicator = "<- AKTUELL (F10?)" if ".sg10" in name or "max_perf" in name else ""
        print(f"{name:<40} | {dt:<20} | {size} {indicator}")

    print("\n💡 HINWEIS:")
    print("Wenn der neueste State (F10) eingefroren ist, kannst du im Emulator")
    print("einfach eine ältere Nummer laden (z.B. F1, F2), falls diese existieren.")

if __name__ == "__main__":
    check_save_states()