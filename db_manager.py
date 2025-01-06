import sqlite3


class DBManager:
    def __init__(self, db_name="schedule.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS employees (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL
                          )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS schedule (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            employee_id INTEGER,
                            day TEXT,
                            start_time TEXT,
                            end_time TEXT,
                            FOREIGN KEY (employee_id) REFERENCES employees (id)
                          )''')
        self.conn.commit()

    def add_employee(self, name):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO employees (name) VALUES (?)", (name,))
        self.conn.commit()

    def fetch_employees(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM employees")
        return cursor.fetchall()

    def delete_employee(self, name):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM employees WHERE name = ?", (name,))
        self.conn.commit()

    def get_employee_id(self, employee_name):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM employees WHERE name = ?", (employee_name,))
        result = cursor.fetchone()
        return result[0] if result else None

    def save_schedule(self, employee_id, day, start_time, end_time):
        cursor = self.conn.cursor()
        # 같은 시간대의 기존 스케줄 삭제
        cursor.execute("""
            DELETE FROM schedule 
            WHERE employee_id = ? AND day = ? AND start_time = ? AND end_time = ?
        """, (employee_id, day, start_time, end_time))

        # 새로운 스케줄 저장
        cursor.execute("""
            INSERT INTO schedule (employee_id, day, start_time, end_time)
            VALUES (?, ?, ?, ?)
        """, (employee_id, day, start_time, end_time))
        self.conn.commit()

    def save_schedule_by_name(self, employee_name, day, start_time, end_time):
        employee_id = self.get_employee_id(employee_name)
        if employee_id:
            self.save_schedule(employee_id, day, start_time, end_time)

    def fetch_schedule(self):
        cursor = self.conn.cursor()
        cursor.execute('''SELECT schedule.id, employees.name, schedule.day, schedule.start_time, schedule.end_time
                          FROM schedule
                          JOIN employees ON schedule.employee_id = employees.id''')
        return cursor.fetchall()

    def clear_schedule(self):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM schedule")
        self.conn.commit()

    def save_time_slots(self, time_slots):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM time_slots")
        for time_slot in time_slots:
            start_time, end_time = time_slot.split('-')
            cursor.execute("INSERT INTO time_slots (start_time, end_time) VALUES (?, ?)", (start_time, end_time))
        self.conn.commit()

    def save_time_slots(self, time_slots):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM time_slots")  # 기존 시간대 삭제
        for time_slot in time_slots:
            start_time, end_time = time_slot.split('-')
            cursor.execute("INSERT INTO time_slots (start_time, end_time) VALUES (?, ?)", (start_time, end_time))
        self.conn.commit()

    def close(self):
        self.conn.close()