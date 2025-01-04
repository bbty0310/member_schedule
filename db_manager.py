import sqlite3

class DBManager:
    def __init__(self, db_name="schedule.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS employees (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            age INTEGER DEFAULT 0
                          )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS schedule (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            employee_id INTEGER,
                            day TEXT,
                            time TEXT,
                            FOREIGN KEY (employee_id) REFERENCES employees (id)
                          )''')
        self.conn.commit()

    def add_employee(self, name, age):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO employees (name, age) VALUES (?, ?)", (name, age))
        self.conn.commit()

    def fetch_employees(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM employees")
        return cursor.fetchall()

    def delete_employee(self, employee_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM employees WHERE id = ?", (employee_id,))
        self.conn.commit()

    def add_schedule(self, employee_id, day, time):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO schedule (employee_id, day, time) VALUES (?, ?, ?)",
                       (employee_id, day, time))
        self.conn.commit()

    def fetch_schedule(self):
        cursor = self.conn.cursor()
        cursor.execute('''SELECT schedule.id, employees.name, schedule.day, schedule.time
                          FROM schedule
                          JOIN employees ON schedule.employee_id = employees.id''')
        return cursor.fetchall()

    def close(self):
        self.conn.close()