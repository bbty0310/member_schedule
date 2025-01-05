from PyQt5.QtWidgets import QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QPushButton, QDialog, \
    QFormLayout, QLineEdit, QDialogButtonBox, QHBoxLayout, QListWidget, QListWidgetItem, QComboBox, QLabel
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDrag, QDropEvent
from db_manager import DBManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DBManager()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("직원 스케줄 관리")
        self.setGeometry(100, 100, 1000, 600)

        # 스케줄 테이블 생성
        self.days = ["월", "화", "수", "목", "금", "토", "일"]
        self.times = [f"{hour:02d}:00-{hour + 1:02d}:00" for hour in range(9, 18)]
        self.table = QTableWidget(len(self.times), len(self.days))
        self.table.setHorizontalHeaderLabels(self.days)
        self.table.setVerticalHeaderLabels(self.times)
        self.table.setAcceptDrops(True)
        self.table.dragEnterEvent = self.drag_enter_event
        self.table.dropEvent = self.drop_event

        # 직원 리스트와 추가 버튼
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

        # 전체 레이아웃 설정 (8:2 비율)
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.table, 8)
        main_layout.addLayout(self.employee_list_layout, 2)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # 스케줄 데이터 로드
        self.load_schedule()
        self.load_employees()

    def load_schedule(self):
        schedules = self.db.fetch_schedule()
        for schedule in schedules:
            name, day, time = schedule[1], schedule[2], schedule[3]
            col = self.days.index(day)
            row = self.times.index(time)
            self.table.setItem(row, col, QTableWidgetItem(name))

    def load_employees(self):
        employees = self.db.fetch_employees()
        for employee in employees:
            self.add_employee_to_ui(employee[1])

    def add_employee_to_ui(self, name):
        item = QListWidgetItem(name)
        item.setData(Qt.UserRole, name)  # 데이터 저장
        self.employee_list.addItem(item)

    def del_employee_to_ui(self):
        selected_items = self.employee_list.selectedItems()  # 선택된 항목 가져오기
        if not selected_items:
            return  # 선택된 항목이 없으면 아무것도 하지 않음
        for item in selected_items:
            self.employee_list.takeItem(self.employee_list.row(item))  # 항목 삭제
            name = item.data(Qt.UserRole)
            self.db.delete_employee(name)  # 데이터베이스에서 직원 삭제

    def export_to_excel(self):
        # 엑셀 내보내기 기능 구현
        import pandas as pd

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

    def drag_enter_event(self, event):
        if event.mimeData().hasText():
            event.accept()
        else:
            event.ignore()

    def drop_event(self, event: QDropEvent):
        if event.mimeData().hasText():
            cursor_text = event.mimeData().text()
            pos = self.table.viewport().mapFromGlobal(event.pos())
            row = self.table.rowAt(pos.y())
            col = self.table.columnAt(pos.x())
            if row != -1 and col != -1:
                existing_item = self.table.item(row, col)
                if existing_item:
                    existing_text = existing_item.text()
                    updated_text = f"{existing_text}, {cursor_text}"
                    self.table.setItem(row, col, QTableWidgetItem(updated_text))
                else:
                    self.table.setItem(row, col, QTableWidgetItem(cursor_text))
            event.accept()
        else:
            event.ignore()

    def manage_employees(self):
        dialog = EmployeeDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            name, age = dialog.get_employee_data()
            self.db.add_employee(name, age)
            self.add_employee_to_ui(name)

    def modify_times(self):
        dialog = TimeDialog(self, self.times)
        if dialog.exec_() == QDialog.Accepted:
            self.times = dialog.get_times()
            self.table.setRowCount(len(self.times))
            self.table.setVerticalHeaderLabels(self.times)

class EmployeeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("직원 관리")
        self.setGeometry(200, 200, 400, 300)
        self.db = parent.db

        # 직원 추가 폼
        self.layout = QVBoxLayout()
        form_layout = QFormLayout()
        self.name_input = QLineEdit()
        self.age_input = QLineEdit()
        form_layout.addRow("이름:", self.name_input)
        form_layout.addRow("나이:", self.age_input)
        self.layout.addLayout(form_layout)

        # 확인 및 취소 버튼
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)
        self.setLayout(self.layout)

    def get_employee_data(self):
        name = self.name_input.text().strip()
        age = int(self.age_input.text().strip()) if self.age_input.text().isdigit() else 0
        return name, age

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
                start_time, end_time = time_range.split("-")
                start_hour, start_minute = start_time.split(":")
                end_hour, end_minute = end_time.split(":")

                row_layout = QHBoxLayout()

                start_hour_cb = QComboBox()
                start_hour_cb.addItems(self.hour_options)
                start_hour_cb.setCurrentText(start_hour)

                start_minute_cb = QComboBox()
                start_minute_cb.addItems(self.minute_options)
                start_minute_cb.setCurrentText(start_minute)

                end_hour_cb = QComboBox()
                end_hour_cb.addItems(self.hour_options)
                end_hour_cb.setCurrentText(end_hour)

                end_minute_cb = QComboBox()
                end_minute_cb.addItems(self.minute_options)
                end_minute_cb.setCurrentText(end_minute)

                self.time_inputs.append((start_hour_cb, start_minute_cb, end_hour_cb, end_minute_cb))

                tilde_label = QLabel("~")
                tilde_label.setAlignment(Qt.AlignCenter)

                # 레이아웃 배치
                row_layout.addWidget(start_hour_cb)
                row_layout.addWidget(start_minute_cb)
                row_layout.addWidget(tilde_label)
                row_layout.addWidget(end_hour_cb)
                row_layout.addWidget(end_minute_cb)

                self.layout.addLayout(row_layout)

        # 확인 및 취소 버튼
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)
        self.setLayout(self.layout)

    def get_times(self):
        times = []
        for start_hour_cb, start_minute_cb, end_hour_cb, end_minute_cb in self.time_inputs:
            start_time = f"{start_hour_cb.currentText()}:{start_minute_cb.currentText()}"
            end_time = f"{end_hour_cb.currentText()}:{end_minute_cb.currentText()}"
            times.append(f"{start_time}-{end_time}")
        return times
