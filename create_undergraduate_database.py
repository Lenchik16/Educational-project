import sqlite3

def create_database():
    # Подключение к базе данных
    conn = sqlite3.connect('undergraduate_programs.db')
    cursor = conn.cursor()

    # Создание таблицы programs
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS programs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        level TEXT,
        code TEXT,
        specialty_type TEXT,
        form TEXT,
        duration TEXT,
        language TEXT,
        total_budget_places INTEGER,
        paid_places TEXT,
        tuition_fee TEXT
    )
    ''')

    # Создание таблицы contacts
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        program_id INTEGER NOT NULL,
        contact_name TEXT NOT NULL,
        contact_email TEXT NOT NULL,
        FOREIGN KEY(program_id) REFERENCES programs(id) ON DELETE CASCADE
    )
    ''')

    # Создание таблицы budget_places
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS budget_places (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        program_id INTEGER,
        quota_type TEXT,
        places INTEGER,
        FOREIGN KEY (program_id) REFERENCES programs (id) ON DELETE CASCADE
    )
    ''')

    # Создание таблицы min_scores
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS min_scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        program_id INTEGER,
        subject TEXT,
        score INTEGER,
        is_mandatory INTEGER,
        FOREIGN KEY (program_id) REFERENCES programs (id) ON DELETE CASCADE
    )
    ''')

    # Создание таблицы passing_scores
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS passing_scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        program_id INTEGER,
        year TEXT,
        score TEXT,
        FOREIGN KEY (program_id) REFERENCES programs (id) ON DELETE CASCADE
    )
    ''')

    # Создание таблицы disciplines
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS disciplines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        program_id INTEGER,
        discipline TEXT,
        FOREIGN KEY (program_id) REFERENCES programs (id) ON DELETE CASCADE
    )
    ''')

    # Создание таблицы professions
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS professions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        program_id INTEGER,
        profession TEXT,
        FOREIGN KEY (program_id) REFERENCES programs (id) ON DELETE CASCADE
    )
    ''')

    # Создание таблицы practice_places
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS practice_places (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        program_id INTEGER,
        place TEXT,
        FOREIGN KEY (program_id) REFERENCES programs (id) ON DELETE CASCADE
    )
    ''')

    # Создание таблицы employment_orgs
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS employment_orgs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        program_id INTEGER,
        org TEXT,
        FOREIGN KEY (program_id) REFERENCES programs (id) ON DELETE CASCADE
    )
    ''')

    # Фиксация изменений и закрытие соединения
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()
    print("База данных успешно создана.")