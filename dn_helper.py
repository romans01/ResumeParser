import sqlite3
import json
import pandas as pd
import openpyxl



def create_tables_and_store_data(json_string, db_path = "data.db"):
    data = json.loads(json_string)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Создаем таблицы
    cur.execute("""
    CREATE TABLE IF NOT EXISTS candidates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        position TEXT,
        degree TEXT,
        institution TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate_id INTEGER,
        category TEXT,
        skill TEXT,
        FOREIGN KEY(candidate_id) REFERENCES candidates(id)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS experience (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate_id INTEGER,
        company TEXT,
        position TEXT,
        duration TEXT,
        FOREIGN KEY(candidate_id) REFERENCES candidates(id)
    )
    """)

    # Извлечение данных из JSON
    name = data.get('name', '')
    position = data.get('position', '')
    education = data.get('education', {})
    degree = education.get('degree', '')
    institution = education.get('institution', '')

    cur.execute("INSERT INTO candidates (name, position, degree, institution) VALUES (?,?,?,?)",
                (name, position, degree, institution))

    candidate_id = cur.lastrowid

    skills = data.get('skills', [])
    for skill in skills:
        category = skill.get('category', '')
        items = skill.get('items', [])
        for item in items:
            cur.execute("INSERT INTO skills (candidate_id, category, skill) VALUES (?,?,?)",
                        (candidate_id, category, item))

    experiences = data.get('experience', [])
    for experience in experiences:
        company = experience.get('company', '')
        position = experience.get('position', '')
        duration = experience.get('duration', '')
        cur.execute("INSERT INTO experience (candidate_id, company, position, duration) VALUES (?,?,?,?)",
                    (candidate_id, company, position, duration))

    conn.commit()
    cur.close()
    conn.close()




def export_to_excel(db_path = "data.db", excel_path="result.xlsx"):
    conn = sqlite3.connect(db_path)

    # Read data from tables
    candidates_df = pd.read_sql_query("SELECT * FROM candidates", conn)
    skills_df = pd.read_sql_query("SELECT * FROM skills", conn)
    #experience_df = pd.read_sql_query("SELECT * FROM experience", conn)

    # Merge data into a single DataFrame
    merged_df = candidates_df.merge(skills_df, left_on='id', right_on='candidate_id', how='left')
    #merged_df = merged_df.merge(experience_df, left_on='candidate_id', right_on='candidate_id', how='left', suffixes=('_skill', '_experience'))

    # Write to Excel
    merged_df.to_excel(excel_path, index=False)

    conn.close()