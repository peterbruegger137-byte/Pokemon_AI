import sqlite3

# Backend nutzt oft pokemon_research.db oder ähnliches
db_files = ["pokemon_research.db", "pokemon_ai.db"]

for db_file in db_files:
    try:
        conn = sqlite3.connect(db_file)
        c = conn.cursor()
        print(f"🛠️ Repariere {db_file}...")
        c.execute("CREATE TABLE IF NOT EXISTS training_stats (id INTEGER PRIMARY KEY, steps TEXT, reward REAL, timestamp TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS map_knowledge (id INTEGER PRIMARY KEY, area_type TEXT, x REAL, y REAL, discovered_at TEXT)")
        conn.commit()
        conn.close()
        print(f"✅ {db_file} ist jetzt bereit.")
    except Exception as e:
        print(f"❌ Konnte {db_file} nicht reparieren: {e}")