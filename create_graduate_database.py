import sqlite3

# Подключение к базе данных
conn = sqlite3.connect('graduate_programs.db')
cursor = conn.cursor()

# Создание таблиц с каскадным удалением
cursor.execute('''CREATE TABLE IF NOT EXISTS Program (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    level TEXT,
    code TEXT,
    specialty_type TEXT,
    study_form TEXT,
    study_duration TEXT,
    language TEXT,
    budget_places TEXT,
    paid_places INTEGER DEFAULT 0,
    tuition_fee TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS Disciplines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    program_id INTEGER NOT NULL,
    discipline_name TEXT NOT NULL,
    FOREIGN KEY(program_id) REFERENCES Program(id) ON DELETE CASCADE
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS Professions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    program_id INTEGER NOT NULL,
    profession_name TEXT NOT NULL,
    FOREIGN KEY(program_id) REFERENCES Program(id) ON DELETE CASCADE
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS Practice (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    program_id INTEGER NOT NULL,
    practice_name TEXT NOT NULL,
    FOREIGN KEY(program_id) REFERENCES Program(id) ON DELETE CASCADE
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS Graduates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    program_id INTEGER NOT NULL,
    graduate_org TEXT NOT NULL,
    FOREIGN KEY(program_id) REFERENCES Program(id) ON DELETE CASCADE
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS Contact (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    program_id INTEGER NOT NULL,
    contact_name TEXT NOT NULL,
    contact_email TEXT NOT NULL,
    FOREIGN KEY(program_id) REFERENCES Program(id) ON DELETE CASCADE
)''')

# Фиксация изменений и закрытие соединения
conn.commit()
conn.close()
print("База данных и таблицы успешно созданы.")