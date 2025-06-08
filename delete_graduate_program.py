import sqlite3
import sys
import os

def delete_program(program_name):
    """Удаляет программу и все связанные данные из базы"""
    try:
        if not os.path.exists('graduate_programs.db'):
            print("❌ Ошибка: База данных 'graduate programs.db' не найдена")
            return False

        conn = sqlite3.connect('graduate programs.db')
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")

        # Находим ID программы
        cursor.execute(
            "SELECT id FROM Program WHERE name = ? COLLATE NOCASE", 
            (program_name,)
        )
        program = cursor.fetchone()
        
        if not program:
            print(f"🔍 Программа '{program_name}' не найдена. Список программ:")
            cursor.execute("SELECT name FROM Program")
            for row in cursor.fetchall():
                print(f"→ {row[0]}")
            return False

        program_id = program[0]

        # Таблицы для очистки (в правильном порядке удаления)
        tables = [
            'Disciplines',    # Дочерние таблицы
            'Professions',
            'Practice',
            'Graduates',
            'Contact',
            'Program'         # Родительская таблица
        ]

        # Удаление данных
        deleted = {}
        for table in tables:
            if table == 'Program':
                query = "DELETE FROM Program WHERE id = ?"
            else:
                query = f"DELETE FROM {table} WHERE program_id = ?"
            
            cursor.execute(query, (program_id,))
            deleted[table] = cursor.rowcount

        conn.commit()
        
        # Результаты удаления
        print("\n✅ Результат удаления:")
        print(f"Программа: {program_name}")
        for table, count in deleted.items():
            if table != 'Program' and count > 0:
                print(f"- Удалено из {table}: {count} записей")

        return True

    except sqlite3.Error as e:
        print(f"🚨 Ошибка базы данных: {str(e)}")
        conn.rollback()
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Использование: python delete.py \"Математические и компьютерные технологии\"")
        sys.exit(1)
    
    program_name = sys.argv[1]
    print(f"Попытка удаления программы: {program_name}")
    if delete_program(program_name):
        print("✅ Удаление завершено успешно")
    else:
        print("❌ Удаление не выполнено")
        sys.exit(1)