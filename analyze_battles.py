import json
import pandas as pd
import os

def bgr_to_rgb(bgr_tuple):
    """Konvertiert BGR (OpenCV/Python) zu RGB (Web/Kotlin)."""
    return (bgr_tuple[2], bgr_tuple[1], bgr_tuple[0])

def run_analysis():
    history_path = "logs_persistent/battle_data.json"
    
    if not os.path.exists(history_path):
        print("❌ Keine Battle-Daten unter logs_persistent gefunden!")
        return

    try:
        with open(history_path, "r") as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Fehler beim Laden der Datei: {e}")
        return
    
    if not data:
        print("⚠ Die Datei ist leer.")
        return

    df = pd.DataFrame(data)

    # --- 1. FUNDORTE (Location Hotspots) ---
    print("\n--- 📍 Top Pokémon Fundorte (Location Hashes) ---")
    location_counts = df['location'].value_counts().head(10)
    print(location_counts)

    # --- 2. FARBANALYSE & OPTIMALE ATTACKEN ---
    # Wir runden die BGR Werte auf 30er Schritte, um ähnliche Farbtöne zu gruppieren
    def simplify_color(color):
        return tuple([round(c / 30) * 30 for c in color])

    df['color_group_bgr'] = df['enemy_color'].apply(simplify_color)
    
    # Berechne die beste Attacke pro Farbgruppe
    # Wir zählen die Häufigkeit jeder Action pro Farbgruppe
    analysis_results = []
    
    for color, group in df.groupby('color_group_bgr'):
        best_action = group['action'].value_counts().index[0]
        win_count = len(group)
        rgb_color = bgr_to_rgb(color)
        
        analysis_results.append({
            "color_bgr": color,
            "color_rgb": rgb_color,
            "hex": '#%02x%02x%02x' % rgb_color,
            "recommended_action": best_action,
            "total_encounters": win_count
        })

    # Sortiere nach Häufigkeit der Begegnungen
    analysis_results = sorted(analysis_results, key=lambda x: x['total_encounters'], reverse=True)

    print("\n--- ⚔ Optimale Attacke pro Gegner-Farbe (Konvertiert zu RGB) ---")
    for res in analysis_results[:10]: # Zeige die Top 10 Typen
        print(f"Farbe {res['hex']} (Begegnungen: {res['total_encounters']}) -> Beste Attacke: {res['recommended_action']}")

    # --- 3. SPEICHERN FÜR KOTLIN DASHBOARD ---
    # Speichert eine saubere JSON für das Frontend
    with open("logs_persistent/dashboard_analytics.json", "w") as f:
        json.dump(analysis_results, f, indent=4)
        
    # Zusätzlich als CSV für Excel/Pandas
    df.to_csv("logs_persistent/training_summary.csv", index=False)
    print("\n✅ Analyse abgeschlossen.")
    print("📊 'dashboard_analytics.json' erstellt (für Kotlin/RGB Anzeige).")

if __name__ == "__main__":
    run_analysis()