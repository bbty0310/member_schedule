from PyQt5.QtWidgets import QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QPushButton, QDialog, \
                            QFormLayout, QLineEdit, QDialogButtonBox, QHBoxLayout, QListWidget, QListWidgetItem
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDrag, QPixmap, QDropEvent
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
        self.table.setDragEnabled(True)

        # 직원 리스트와 추가 버튼
        self.employee_list_layout = QVBoxLayout()
        self.employee_list = QListWidget()
        self.employee_list.setDragEnabled(True)  # 드래그 활성화
        self.employee_list.setStyleSheet("background-color: #f0f0f0; border: 1px solid gray;")
        self.employee_list.setFixedHeight(400)

        self.add_employee_button = QPushButton("직원 추가")
        self.add_employee_button.clicked.connect(self.manage_employees)


        self.delete_employee_button = QPushButton("직원 삭제")
        self.delete_employee_button.clicked.connect(self.del_employee_to_ui)

        self.employee_list_layout.addWidget(self.employee_list)
        self.employee_list_layout.addWidget(self.add_employee_button)
        self.employee_list_layout.addWidget(self.delete_employee_button)

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

    def del_employee_to_ui(self, name):
        if item := self.employee_list.findItems(name, Qt.MatchExactly):
            self.employee_list.takeItem(self.employee_list.row(item[0]))

    def manage_employees(self):
        dialog = EmployeeDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            name = dialog.get_employee_data()
            self.db.add_employee(name)
            self.add_employee_to_ui(name)

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
        self.layout.addLayout(form_layout)

        # 확인 및 취소 버튼
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)
        self.setLayout(self.layout)

    def get_employee_data(self):
        name = self.name_input.text().strip()
        return name
