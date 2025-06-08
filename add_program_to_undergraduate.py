import sqlite3
import re
import sys

# Подключение к базе данных
conn = sqlite3.connect('undergraduate_programs.db')
cursor = conn.cursor()

def parse_program(text):
    """
    Парсит текст программы и возвращает структурированный словарь.
    Разбиваем по секциям, затем для каждой секции вызываем соответствующий парсер.
    """
    section_titles = [
        'Общая информация',
        'Минимальные баллы ЕГЭ',
        'Проходные баллы прошлых лет',
        'Основные дисциплины',
        'Возможные профессии',
        'Места практики',
        'Организации для трудоустройства',
        'Контактное лицо'
    ]
    program = {}
    lines = text.strip().split('\n')
    current_section = None
    section_content = []

    for raw_line in lines:
        line = raw_line.strip()
        for title in section_titles:
            if line.startswith(title):
                if current_section is not None:
                    program[current_section] = section_content
                current_section = title
                section_content = []
                if len(line) > len(title):
                    remaining = line[len(title):].strip()
                    if remaining:
                        section_content.append(remaining)
                break
        else:
            if line:
                section_content.append(line)

    if current_section is not None:
        program[current_section] = section_content

    program_data = {
        'general_info': {
            'Название программы': "Нет информации",
            'Уровень': "Нет информации",
            'Код направления': "Нет информации",
            'Тип специальности': "Нет информации",
            'Форма обучения': "Нет информации",
            'Срок обучения': "Нет информации",
            'Язык обучения': "Нет информации",
            'Стоимость обучения': "Нет информации",
            'total_budget_places': 0,
            'paid_places': 0,
            'budget_places_details': []
        },
        'min_scores': [],
        'passing_scores': [],
        'disciplines': ["Нет информации"],
        'professions': ["Нет информации"],
        'practice_places': ["Нет информации"],
        'employment_orgs': ["Нет информации"],
        'contacts': []
    }

    if 'Общая информация' in program:
        parsed_info = parse_general_info(program['Общая информация'])
        if parsed_info is not None:
            program_data['general_info'] = parsed_info

    if 'Минимальные баллы ЕГЭ' in program:
        parsed_scores = parse_min_scores(program['Минимальные баллы ЕГЭ'])
        if parsed_scores:
            program_data['min_scores'] = parsed_scores

    if 'Проходные баллы прошлых лет' in program:
        parsed_passing = parse_passing_scores(program['Проходные баллы прошлых лет'])
        if parsed_passing:
            program_data['passing_scores'] = parsed_passing

    if 'Основные学科' in program:
        parsed_disciplines = parse_list(program['Основные дисциплины'])
        if parsed_disciplines:
            program_data['disciplines'] = parsed_disciplines

    if 'Возможные профессии' in program:
        parsed_professions = parse_list(program['Возможные профессии'])
        if parsed_professions:
            program_data['professions'] = parsed_professions

    if 'Места практики' in program:
        parsed_practice = parse_list(program['Места практики'])
        if parsed_practice:
            program_data['practice_places'] = parsed_practice

    if 'Организации для трудоустройства' in program:
        parsed_orgs = parse_list(program['Организации для трудоустройства'])
        if parsed_orgs:
            program_data['employment_orgs'] = parsed_orgs

    if 'Контактное лицо' in program:
        parsed_contacts = parse_contacts(program['Контактное лицо'])
        if parsed_contacts:
            program_data['contacts'] = parsed_contacts

    return program_data

def parse_general_info(lines):
    """
    Парсит секцию «Общая информация» в виде словаря.
    """
    info = {
        'Название программы': "Нет информации",
        'Уровень': "Нет информации",
        'Код направления': "Нет информации",
        'Тип специальности': "Нет информации",
        'Форма обучения': "Нет информации",
        'Срок обучения': "Нет информации",
        'Язык обучения': "Нет информации",
        'Стоимость обучения': "Нет информации",
        'total_budget_places': 0,
        'paid_places': 0,
        'budget_places_details': []
    }
    budget_places_details = []
    total_budget_places = 0
    collecting_details = False

    for raw_line in lines:
        line = raw_line.strip()
        m_budget = re.match(r'Бюджетные\s+места\s*:\s*(\d+)', line, flags=re.IGNORECASE)
        if m_budget:
            total_budget_places = int(m_budget.group(1))
            collecting_details = True
            continue

        if collecting_details:
            m_detail = re.match(r'(\d+)\s+мест[а]?[\s—-]+\s*(.+)', line)
            if m_detail:
                places = int(m_detail.group(1))
                quota_type = m_detail.group(2).strip()
                budget_places_details.append((places, quota_type))
                continue
            else:
                collecting_details = False

        m_paid = re.match(r'Платные\s+места\s*:\s*(\d+)', line, flags=re.IGNORECASE)
        if m_paid:
            info['paid_places'] = int(m_paid.group(1))
            continue

        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            if not key.lower().startswith('бюджетные места') and not key.lower().startswith('платные места'):
                info[key] = value

    info['total_budget_places'] = total_budget_places
    info['budget_places_details'] = budget_places_details
    return info

def parse_min_scores(lines):
    """
    Парсит минимальные баллы ЕГЭ.
    """
    scores = []
    for raw_line in lines:
        line = raw_line.strip()
        if ':' in line:
            subject, score = line.split(':', 1)
            subject = subject.strip()
            score = score.strip()
            if score.isdigit():
                scores.append((subject, int(score)))
    if not scores:
        return []
    if len(scores) == 1:
        return [(scores[0][0], scores[0][1], 1)]
    result = []
    result.append((scores[0][0], scores[0][1], 1))
    for subj, sc in scores[1:-1]:
        result.append((subj, sc, 0))
    result.append((scores[-1][0], scores[-1][1], 1))
    return result

def parse_passing_scores(lines):
    """
    Парсит проходные баллы прошлых лет.
    """
    scores = []
    for raw_line in lines:
        line = raw_line.strip()
        if ':' in line:
            year, score = line.split(':', 1)
            year = year.strip()
            score = score.strip()
            if score.isdigit():
                scores.append((year, int(score)))
    return scores

def parse_list(lines):
    """
    Парсит простые списки (дисциплины, профессии, места практики и т.д.).
    """
    result = []
    for raw_line in lines:
        line = raw_line.strip()
        if line:
            result.append(line)
    return result

def parse_contacts(lines):
    """
    Парсит контактное лицо.
    """
    contacts = []
    current_name = None
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        if line.lower().startswith("e-mail"):
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

def insert_program(program):
    """
    Вставляет разобранную программу в таблицы базы данных.
    """
    general_info = program.get('general_info', {})
    name = general_info.get('Название программы', "Нет информации")
    level = general_info.get('Уровень', "Нет информации")
    code = general_info.get('Код направления', "Нет информации")
    specialty_type = general_info.get('Тип специальности', "Нет информации")
    form = general_info.get('Форма обучения', "Нет информации")
    duration = general_info.get('Срок обучения', "Нет информации")
    language = general_info.get('Язык обучения', "Нет информации")
    total_budget_places = general_info.get('total_budget_places', 0)
    paid_places = general_info.get('paid_places', 0)
    tuition_fee = general_info.get('Стоимость обучения', "Нет информации")

    cursor.execute('''
        INSERT INTO programs 
          (name, level, code, specialty_type, form, duration, language, total_budget_places, paid_places, tuition_fee)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, level, code, specialty_type, form, duration, language, total_budget_places, paid_places, tuition_fee))

    program_id = cursor.lastrowid

    contacts = program.get('contacts', [])
    if not contacts:
        contacts.append({"name": "Нет информации", "email": "Нет информации"})
    for contact in contacts:
        cursor.execute('''
            INSERT INTO contacts (program_id, contact_name, contact_email)
            VALUES (?, ?, ?)
        ''', (program_id, contact.get('name', "Нет информации"), contact.get('email', "Нет информации")))

    for places, quota_type in general_info.get('budget_places_details', []):
        cursor.execute(
            'INSERT INTO budget_places (program_id, quota_type, places) VALUES (?, ?, ?)',
            (program_id, quota_type, places)
        )

    for subject, score, is_mandatory in program.get('min_scores', []):
        cursor.execute(
            'INSERT INTO min_scores (program_id, subject, score, is_mandatory) VALUES (?, ?, ?, ?)',
            (program_id, subject, score, is_mandatory)
        )

    for year, score in program.get('passing_scores', []):
        cursor.execute(
            'INSERT INTO passing_scores (program_id, year, score) VALUES (?, ?, ?)',
            (program_id, year, score)
        )

    for discipline in program.get('disciplines', ["Нет информации"]):
        cursor.execute(
            'INSERT INTO disciplines (program_id, discipline) VALUES (?, ?)',
            (program_id, discipline)
        )

    for profession in program.get('professions', ["Нет информации"]):
        cursor.execute(
            'INSERT INTO professions (program_id, profession) VALUES (?, ?)',
            (program_id, profession)
        )

    for place in program.get('practice_places', ["Нет информации"]):
        cursor.execute(
            'INSERT INTO practice_places (program_id, place) VALUES (?, ?)',
            (program_id, place)
        )

    for org in program.get('employment_orgs', ["Нет информации"]):
        cursor.execute(
            'INSERT INTO employment_orgs (program_id, org) VALUES (?, ?)',
            (program_id, org)
        )

    conn.commit()

def main():
    """
    Основная функция: считываем данные из stdin и добавляем их в базу данных.
    """
    print("Вставьте текст программы. Для завершения ввода нажмите Ctrl + Z (Windows) или Ctrl + D (Unix).")
    lines = []
    try:
        while True:
            line = input()
            lines.append(line)
    except EOFError:
        pass

    input_text = "\n".join(lines)
    if input_text.strip():
        program_data = parse_program(input_text)
        insert_program(program_data)
        print("Программа успешно добавлена в базу данных.")
    else:
        print("Вы не ввели текст программы.")

if __name__ == "__main__":
    main()
    conn.close()