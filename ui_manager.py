from PyQt5.QtWidgets import QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QPushButton, QDialog, \
    QFormLayout, QLineEdit, QDialogButtonBox, QHBoxLayout, QListWidget, QListWidgetItem, QComboBox, QLabel, QMenuBar, QMenu, QAction
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDrag, QDropEvent
from db_manager import DBManager
import pandas as pd


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DBManager()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("직원 스케줄 관리")
        self.setGeometry(100, 100, 1000, 600)

        self.days = ["월", "화", "수", "목", "금", "토", "일"]
        self.times = [f"{hour:02d}:00-{hour + 1:02d}:00" for hour in range(9, 18)]
        self.table = QTableWidget(len(self.times), len(self.days))
        self.table.setHorizontalHeaderLabels(self.days)
        self.table.setVerticalHeaderLabels(self.times)
        self.table.setAcceptDrops(True)

        self.employee_list_layout = QVBoxLayout()
        self.employee_list = QListWidget()
        self.employee_list.setDragEnabled(True)
        self.employee_list.setStyleSheet("background-color: #f0f0f0; border: 1px solid gray;")
        self.employee_list.setFixedHeight(400)

        self.add_employee_button = QPushButton("직원 추가")
        self.add_employee_button.clicked.connect(self.manage_employees)
        self.employee_list_layout.addWidget(self.employee_list)
        self.employee_list_layout.addWidget(self.add_employee_button)

        self.delete_employee_button = QPushButton("직원 삭제")
        self.delete_employee_button.clicked.connect(self.del_employee_to_ui)
        self.employee_list_layout.addWidget(self.delete_employee_button)

        self.export_to_excel_button = QPushButton("엑셀로 내보내기")
        self.export_to_excel_button.clicked.connect(self.export_to_excel)
        self.employee_list_layout.addWidget(self.export_to_excel_button)

        self.modify_time_button = QPushButton("시간 수정")
        self.modify_time_button.clicked.connect(self.modify_times)
        self.employee_list_layout.addWidget(self.modify_time_button)

        menubar = self.menuBar()
        file_menu = menubar.addMenu('파일')

        # 저장 액션 생성
        save_action = QAction('저장', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_all)

        # 메뉴에 저장 액션 추가
        file_menu.addAction(save_action)

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.table, 8)
        main_layout.addLayout(self.employee_list_layout, 2)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.load_schedule()
        self.load_employees()

    def load_schedule(self):
        schedules = self.db.fetch_schedule()
        for schedule in schedules:
            _, name, day, start_time, end_time = schedule
            col = self.days.index(day)
            time_range = f"{start_time}-{end_time}"
            row = self.times.index(time_range)
            self.table.setItem(row, col, QTableWidgetItem(name))

    def load_employees(self):
        employees = self.db.fetch_employees()
        for employee in employees:
            self.add_employee_to_ui(employee[1])

    def add_employee_to_ui(self, name):
        item = QListWidgetItem(name)
        item.setData(Qt.UserRole, name)
        self.employee_list.addItem(item)

    def del_employee_to_ui(self):
        selected_items = self.employee_list.selectedItems()
        if not selected_items:
            return
        for item in selected_items:
            self.employee_list.takeItem(self.employee_list.row(item))
            name = item.data(Qt.UserRole)
            self.db.delete_employee(name)

    def export_to_excel(self):
        data = []
        for row in range(self.table.rowCount()):
            row_data = []
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                row_data.append(item.text() if item else "")
            data.append(row_data)

        df = pd.DataFrame(data, columns=self.days, index=self.times)
        file_path = "schedule.xlsx"
        df.to_excel(file_path)
        print(f"스케줄이 {file_path}에 저장되었습니다.")

    def manage_employees(self):
        dialog = EmployeeDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            name = dialog.get_employee_data()
            self.db.add_employee(name)
            self.add_employee_to_ui(name)

    def modify_times(self):
        dialog = TimeDialog(self, self.times)
        if dialog.exec_() == QDialog.Accepted:
            self.times = dialog.get_times()
            self.table.setRowCount(len(self.times))
            self.table.setVerticalHeaderLabels(self.times)

    def save_all(self):
        self.db.clear_schedule()

        for row in range(self.table.rowCount()):
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and item.text():
                    employee_name = item.text()
                    day = self.days[col]
                    time_range = self.times[row]
                    start_time, end_time = time_range.split('-')
                    employee = next((emp for emp in self.db.fetch_employees() if emp[1] == employee_name), None)
                    if employee:
                        self.db.save_schedule(employee[0], day, start_time, end_time)

        # 시간 저장
        self.db.save_time_slots(self.times)

        print("모든 변경사항이 저장되었습니다.")


class EmployeeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("직원 관리")
        self.setGeometry(200, 200, 400, 300)
        self.db = parent.db

        self.layout = QVBoxLayout()
        form_layout = QFormLayout()
        self.name_input = QLineEdit()
        form_layout.addRow("이름:", self.name_input)
        self.layout.addLayout(form_layout)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)
        self.setLayout(self.layout)

    def get_employee_data(self):
        return self.name_input.text().strip()


class TimeDialog(QDialog):
    def __init__(self, parent=None, current_times=None):
        super().__init__(parent)
        self.setWindowTitle("시간 수정")
        self.setGeometry(200, 200, 400, 400)
        self.layout = QVBoxLayout()
        self.time_inputs = []
        self.hour_options = [f"{i:02d}" for i in range(24)]
        self.minute_options = [f"{i:02d}" for i in range(0, 60, 15)]

        if current_times:
            for time_range in current_times:
                self.add_time_row(time_range)

        button_layout = QHBoxLayout()

        self.add_time_button = QPushButton("+")
        self.del_time_button = QPushButton("-")
        self.add_time_button.clicked.connect(self.add_time_row)
        self.del_time_button.clicked.connect(self.del_time_row)

        button_layout.addWidget(self.add_time_button)
        button_layout.addWidget(self.del_time_button)

        self.layout.addLayout(button_layout)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)

        self.setLayout(self.layout)

    def add_time_row(self, time_range=None):
        row_layout = QHBoxLayout()
        start_hour_cb = QComboBox()
        start_hour_cb.addItems(self.hour_options)
        start_minute_cb = QComboBox()
        start_minute_cb.addItems(self.minute_options)
        end_hour_cb = QComboBox()
        end_hour_cb.addItems(self.hour_options)
        end_minute_cb = QComboBox()
        end_minute_cb.addItems(self.minute_options)

        if time_range:
            start_time, end_time = time_range.split("-")
            start_hour, start_minute = start_time.split(":")
            end_hour, end_minute = end_time.split(":")
            start_hour_cb.setCurrentText(start_hour)
            start_minute_cb.setCurrentText(start_minute)
            end_hour_cb.setCurrentText(end_hour)
            end_minute_cb.setCurrentText(end_minute)
        else:
            start_hour_cb.setCurrentText("09")
            start_minute_cb.setCurrentText("00")
            end_hour_cb.setCurrentText("10")
            end_minute_cb.setCurrentText("00")

        self.time_inputs.append((start_hour_cb, start_minute_cb, end_hour_cb, end_minute_cb))

        tilde_label = QLabel("~")
        tilde_label.setAlignment(Qt.AlignCenter)

        row_layout.addWidget(start_hour_cb)
        row_layout.addWidget(start_minute_cb)
        row_layout.addWidget(tilde_label)
        row_layout.addWidget(end_hour_cb)
        row_layout.addWidget(end_minute_cb)

        self.layout.insertLayout(self.layout.count() - 2, row_layout)

    def del_time_row(self):
        if not self.time_inputs:
            return

        self.time_inputs.pop()

        for i in range(self.layout.count() - 3, -1, -1):
            item = self.layout.itemAt(i)
            if isinstance(item, QHBoxLayout):
                row_layout = item
                break
        else:
            return

        while row_layout.count():
            item = row_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
        # 행 제거
        self.layout.removeItem(row_layout)

    def get_times(self):
        times = []
        for start_hour_cb, start_minute_cb, end_hour_cb, end_minute_cb in self.time_inputs:
            start_time = f"{start_hour_cb.currentText()}:{start_minute_cb.currentText()}"
            end_time = f"{end_hour_cb.currentText()}:{end_minute_cb.currentText()}"
            times.append(f"{start_time}-{end_time}")
        return times
