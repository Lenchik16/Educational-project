import sqlite3
import sys

# Подключение к базе данных
conn = sqlite3.connect('graduate_programs.db')
cursor = conn.cursor()

# Список известных секций
known_sections = [
    "Общая информация",
    "Ключевые дисциплины",
    "Возможные профессии",
    "Места практики",
    "Организации, в которых работают выпускники",
    "Контактное лицо"
]

def parse_input(text):
    sections = {}
    current_section = None

    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue
        if line in known_sections:
            current_section = line
            sections[current_section] = []
        elif current_section:
            sections[current_section].append(line)
    
    return sections

def process_contacts(lines):
    contacts = []
    current_name = None

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("e-mail:"):
            if current_name:
                email = line.split(":", 1)[1].strip()
                contacts.append({"name": current_name, "email": email})
                current_name = None
        else:
            if current_name:
                contacts.append({"name": current_name, "email": "Нет информации"})
            current_name = line
    
    if current_name:
        contacts.append({"name": current_name, "email": "Нет информации"})
    
    return contacts

def process_general_info(lines):
    general_data = {}
    for line in lines:
        if ':' in line:
            key, value = map(str.strip, line.split(':', 1))
            general_data[key] = value
    return general_data

def safe_int(value, default=0):
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

# Основная обработка
if __name__ == "__main__":
    print("Введите текст программы (Ctrl+Z/Ctrl+D для завершения):")
    input_text = sys.stdin.read()

    sections = parse_input(input_text)
    
    data = {
        "general": {},
        "disciplines": [],
        "professions": [],
        "practice": [],
        "graduates": [],
        "contacts": []
    }

    for section_name, lines in sections.items():
        if section_name == "Общая информация":
            data["general"] = process_general_info(lines)
        elif section_name == "Ключевые дисциплины":
            data["disciplines"] = [line.strip() for line in lines if line.strip()]
        elif section_name == "Возможные профессии":
            data["professions"] = [line.strip() for line in lines if line.strip()]
        elif section_name == "Места практики":
            data["practice"] = [line.strip() for line in lines if line.strip()]
        elif section_name == "Организации, в которых работают выпускники":
            data["graduates"] = [line.strip() for line in lines if line.strip()]
        elif section_name == "Контактное лицо":
            data["contacts"] = process_contacts(lines)

    # Вставка основной информации
    budget_value = data["general"].get("Бюджетные места", "-")
    program_fields = {
        "name": data["general"].get("Название программы", ""),
        "level": data["general"].get("Уровень", ""),
        "code": data["general"].get("Код направления", ""),
        "specialty_type": data["general"].get("Тип специальности", ""),
        "study_form": data["general"].get("Форма обучения", ""),
        "study_duration": data["general"].get("Срок обучения", ""),
        "language": data["general"].get("Язык обучения", ""),
        "budget_places": "-" if budget_value == "0" else budget_value,
        "paid_places": safe_int(data["general"].get("Платные места", 0)),
        "tuition_fee": data["general"].get("Стоимость обучения", "")
    }

    cursor.execute('''INSERT INTO Program (
        name, level, code, specialty_type, study_form,
        study_duration, language, budget_places, paid_places, tuition_fee
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', tuple(program_fields.values()))

    program_id = cursor.lastrowid
    print(f"\nДобавлена программа ID {program_id}: {program_fields['name']}")

    # Вспомогательная функция для вставки данных
    def insert_batch(table, field, items):
        if items:
            cursor.executemany(
                f'INSERT INTO {table} (program_id, {field}) VALUES (?, ?)',
                [(program_id, item) for item in items]
            )
            print(f"Добавлено {len(items)} записей в {table}")

    # Вставка связанных данных
    insert_batch('Pivot', 'discipline_name', data["disciplines"])
    insert_batch('Professions', 'profession_name', data["professions"])
    insert_batch('Practice', 'practice_name', data["practice"])
    insert_batch('Graduates', 'graduate_org', data["graduates"])

    # Обработка контактов
    if not data["contacts"]:
        data["contacts"].append({
            "name": "Нет информации",
            "email": "Нет информации"
        })

    for contact in data["contacts"]:
        cursor.execute('''INSERT INTO Contact 
            (program_id, contact_name, contact_email)
            VALUES (?, ?, ?)''',
            (program_id, 
             contact.get("name", "Нет информации"),
             contact.get("email", "Нет информации"))
        )
    print(f"Добавлено {len(data['contacts'])} контактов")

    # Фиксация изменений и закрытие соединения
    conn.commit()
    conn.close()
    print("\nВсе данные успешно сохранены в базе данных!")