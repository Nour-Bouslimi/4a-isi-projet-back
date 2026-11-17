"""Crée poleatheck.db à partir de db/schema.sql (et db/seed.sql si --seed)."""
import os
import sqlite3
import sys

DB_FILE = "poleatheck.db"

if os.path.exists(DB_FILE):
    os.remove(DB_FILE)

conn = sqlite3.connect(DB_FILE)
with open(os.path.join("db", "schema.sql"), encoding="utf-8") as f:
    conn.executescript(f.read())
print("Schéma créé")

# Insertion des données de test si l'option --seed est spécifiée
seed = os.path.join("db", "seed.sql")
if "--seed" in sys.argv and os.path.exists(seed):
    with open(seed, encoding="utf-8") as f:
        conn.executescript(f.read())
    print("Données de test insérées")

conn.commit()
conn.close()