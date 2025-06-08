import sqlite3
import sys
import os

def delete_program(program_name):
    """Удаляет программу и все связанные данные из базы"""
    try:
        # Проверка существования базы данных
        if not os.path.exists('undergraduate_programs.db'):
            print("❌ Ошибка: База данных 'undergraduate_programs.db' не найдена")
            return False

        # Подключение к базе данных
        conn = sqlite3.connect('undergraduate_programs.db')
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")  # Включение поддержки внешних ключей

        # Поиск ID программы по названию
        cursor.execute(
            "SELECT id FROM programs WHERE name = ? COLLATE NOCASE", 
            (program_name,)
        )
        program = cursor.fetchone()
        
        # Если программа не найдена
        if not program:
            print(f"🔍 Программа '{program_name}' не найдена. Список программ:")
            cursor.execute("SELECT name FROM programs")
            for row in cursor.fetchall():
                print(f"→ {row[0]}")
            return False

        program_id = program[0]

        # Список таблиц для очистки (дочерние таблицы + родительская)
        tables = [
            'contacts',          # Контакты
            'budget_places',     # Бюджетные места
            'min_scores',        # Минимальные баллы
            'passing_scores',    # Проходные баллы
            'disciplines',       # Дисциплины
            'professions',       # Профессии
            'practice_places',   # Места практики
            'employment_orgs',   # Организации для трудоустройства
            'programs'           # Родительская таблица
        ]

        # Удаление данных из таблиц
        deleted = {}
        for table in tables:
            if table == 'programs':
                query = "DELETE FROM programs WHERE id = ?"
            else:
                query = f"DELETE FROM {table} WHERE program_id = ?"
            
            cursor.execute(query, (program_id,))
            deleted[table] = cursor.rowcount

        # Фиксация изменений
        conn.commit()
        
        # Вывод результатов удаления
        print("\n✅ Результат удаления:")
        print(f"Программа: {program_name}")
        for table, count in deleted.items():
            if table != 'programs' and count > 0:
                print(f"- Удалено из {table}: {count} записей")

        return True

    except sqlite3.Error as e:
        # Обработка ошибок базы данных
        print(f"🚨 Ошибка базы данных: {str(e)}")
        conn.rollback()
        return False
    finally:
        # Закрытие соединения
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    # Проверка аргументов командной строки
    if len(sys.argv) != 2:
        print("Использование: python delete.py \"Название программы\"")
        sys.exit(1)
    
    program_name = sys.argv[1]
    print(f"Попытка удаления программы: {program_name}")
    if delete_program(program_name):
        print("✅ Удаление завершено успешно")
    else:
        print("❌ Удаление не выполнено")
        sys.exit(1)