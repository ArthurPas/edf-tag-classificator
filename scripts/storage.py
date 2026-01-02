import json
import sqlite3

DB_NAME = "data/rf_finder.db"
TABLE_NAME = "rf_file"
JS_FILE = "data/rf_database.js"
COL_KEY = 'path'
COL_VALUE = 'tag'
def initialize_db(dbname=DB_NAME):
    con = sqlite3.connect(dbname)
    cur = con.cursor()  
    cur.execute(f"CREATE TABLE IF NOT EXISTS {TABLE_NAME}(id INTEGER PRIMARY KEY, {COL_KEY} TEXT, {COL_VALUE} TEXT)")
    cur.close()
    con.commit()
def store_tag(file_path, tag):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()  
    cur.execute(f"INSERT INTO {TABLE_NAME} (path, tag) VALUES (?, ?)", (file_path, tag))
    cur.close()
    con.commit()
    con.close()

import sqlite3
import json


def convert_db_to_js():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        print(f"Lecture de la table '{TABLE_NAME}'...")
        # On sélectionne les colonnes configurées plus haut
        query = f"SELECT {COL_KEY}, {COL_VALUE} FROM {TABLE_NAME}"
        cursor.execute(query)
        rows = cursor.fetchall()

        # Dictionnaire où chaque clé contient une LISTE de valeurs
        data_dict = {}
        
        for row in rows:
            key = row[0]
            val = row[1]
            
            if key:
                # Si la clé n'existe pas encore, on initialise une liste vide
                if key not in data_dict:
                    data_dict[key] = []
                
                # On ajoute la valeur à la liste (si elle n'est pas null)
                if val:
                    data_dict[key].append(val)

        conn.close()

        # Formatage JSON avec indentation pour lisibilité
        json_str = json.dumps(data_dict, ensure_ascii=False, indent=2)
        
        # Création du contenu final du fichier JS
        js_content = f"const DATABASE = {json_str};"

        with open(JS_FILE, 'w', encoding='utf-8') as f:
            f.write(js_content)

        print(f"Succès ! {len(data_dict)} clés exportées dans '{JS_FILE}'.")

    except sqlite3.Error as e:
        print(f"Erreur SQLite: {e}")
    except Exception as e:
        print(f"Erreur générale: {e}")

if __name__ == "__main__":
    convert_db_to_js()