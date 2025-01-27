import sys
import pymysql
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel, \
    QTableWidget, QTableWidgetItem, QDialog, QMessageBox
import config  # Импортируем конфигурацию


# Подключение к базе данных MySQL через PyMySQL с использованием конфигурации из config.py
def connect_db():
    try:
        db_config = config.DB_CONFIG  # Получаем настройки подключения
        return pymysql.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database'],
            charset=db_config['charset']
        )
    except pymysql.MySQLError as e:
        print(f"Ошибка при подключении к базе данных: {e}")
        return None


# Аутентификация пользователя
def authenticate_user(username, password):
    conn = connect_db()
    if not conn:
        return None  # Если соединение не удалось, возвращаем None

    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        return user if user and user[2] == password else None
    except pymysql.MySQLError as e:
        print(f"Ошибка при выполнении запроса: {e}")
        return None
    finally:
        conn.close()


# Получение данных об огнетушителях
def get_fire_extinguishers():
    conn = connect_db()
    if not conn:
        return []  # Если соединение не удалось, возвращаем пустой список

    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM fire_extinguishers")
        extinguishers = cursor.fetchall()
        return extinguishers
    except pymysql.MySQLError as e:
        print(f"Ошибка при выполнении запроса: {e}")
        return []
    finally:
        conn.close()


# Добавление нового огнетушителя в базу данных
def add_fire_extinguisher(number, cabinet, expiration_date, needs_replacement):
    conn = connect_db()
    if not conn:
        print("Ошибка подключения к базе данных!")
        return  # Если соединение не удалось, прерываем выполнение функции

    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO fire_extinguishers (number, cabinet, expiration_date, needs_replacement)
            VALUES (%s, %s, %s, %s)
        """, (number, cabinet, expiration_date, needs_replacement))
        conn.commit()
    except pymysql.MySQLError as e:
        print(f"Ошибка при выполнении запроса: {e}")
    finally:
        conn.close()


class MainWindow(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Информационная система для учета огнетушителей')
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        # Кнопка для отображения огнетушителей
        self.fire_extinguishers_button = QPushButton('Все огнетушители', self)
        self.fire_extinguishers_button.setEnabled(False)  # Изначально кнопка неактивна
        self.fire_extinguishers_button.clicked.connect(self.show_fire_extinguishers)
        layout.addWidget(self.fire_extinguishers_button)

        # Кнопка для добавления огнетушителей (только для администратора)
        if self.user[3] == 'admin':
            self.add_extinguisher_button = QPushButton('Добавить огнетушитель', self)
            self.add_extinguisher_button.clicked.connect(self.add_fire_extinguisher)
            layout.addWidget(self.add_extinguisher_button)

        # Кнопка для выхода из программы
        self.logout_button = QPushButton('Выход', self)
        self.logout_button.clicked.connect(self.close)
        layout.addWidget(self.logout_button)

        self.setLayout(layout)

        # Применяем стиль к кнопке
        self.fire_extinguishers_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)

        # После авторизации активируем кнопку "Все огнетушители"
        self.fire_extinguishers_button.setEnabled(True)

    def show_fire_extinguishers(self):
        extinguishers = get_fire_extinguishers()
        if not extinguishers:
            QMessageBox.warning(self, 'Ошибка', 'Не удалось загрузить данные об огнетушителях!')
            return

        table = QTableWidget()
        table.setRowCount(len(extinguishers))
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(['Номер', 'Кабинет', 'Годен до', 'Требуется замена'])

        for i, ext in enumerate(extinguishers):
            table.setItem(i, 0, QTableWidgetItem(ext[1]))  # Номер огнетушителя
            table.setItem(i, 1, QTableWidgetItem(ext[2]))  # Кабинет
            table.setItem(i, 2, QTableWidgetItem(str(ext[3])))  # Годен до (дата)
            table.setItem(i, 3, QTableWidgetItem('Да' if ext[4] else 'Нет'))  # Требуется замена

        table.show()  # Показываем таблицу с огнетушителями

    def add_fire_extinguisher(self):
        dialog = AddFireExtinguisherDialog(self)
        dialog.exec_()


class AddFireExtinguisherDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Добавить огнетушитель")
        self.setGeometry(200, 200, 400, 300)

        layout = QVBoxLayout()

        self.number_label = QLabel('Номер огнетушителя:', self)
        self.number_input = QLineEdit(self)
        layout.addWidget(self.number_label)
        layout.addWidget(self.number_input)

        self.cabinet_label = QLabel('Кабинет:', self)
        self.cabinet_input = QLineEdit(self)
        layout.addWidget(self.cabinet_label)
        layout.addWidget(self.cabinet_input)

        self.expiration_label = QLabel('Годен до (ГГГГ-ММ-ДД):', self)
        self.expiration_input = QLineEdit(self)
        layout.addWidget(self.expiration_label)
        layout.addWidget(self.expiration_input)

        self.replacement_label = QLabel('Требуется замена:', self)
        self.replacement_button_yes = QPushButton('Да', self)
        self.replacement_button_yes.clicked.connect(self.set_replacement_yes)
        self.replacement_button_no = QPushButton('Нет', self)
        self.replacement_button_no.clicked.connect(self.set_replacement_no)
        layout.addWidget(self.replacement_label)
        layout.addWidget(self.replacement_button_yes)
        layout.addWidget(self.replacement_button_no)

        self.save_button = QPushButton('Сохранить', self)
        self.save_button.clicked.connect(self.save_fire_extinguisher)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

        self.needs_replacement = 0  # по умолчанию "Нет" (0)

    def set_replacement_yes(self):
        self.needs_replacement = 1  # "Да"
        self.replacement_button_yes.setStyleSheet("background-color: lightgreen;")
        self.replacement_button_no.setStyleSheet("")

    def set_replacement_no(self):
        self.needs_replacement = 0  # "Нет"
        self.replacement_button_no.setStyleSheet("background-color: lightcoral;")
        self.replacement_button_yes.setStyleSheet("")

    def save_fire_extinguisher(self):
        number = self.number_input.text()
        cabinet = self.cabinet_input.text()
        expiration_date = self.expiration_input.text()

        # Сохраняем данные в базу данных
        add_fire_extinguisher(number, cabinet, expiration_date, self.needs_replacement)

        QMessageBox.information(self, 'Успех', 'Огнетушитель добавлен!')
        self.close()


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Авторизация")
        self.setGeometry(100, 100, 400, 250)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.username_label = QLabel('Логин:', self)
        self.username_input = QLineEdit(self)
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)

        self.password_label = QLabel('Пароль:', self)
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)

        self.login_button = QPushButton('Войти', self)
        self.login_button.clicked.connect(self.login)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        user = authenticate_user(username, password)
        if user:
            self.close()
            self.main_window = MainWindow(user)
            self.main_window.show()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Неверный логин или пароль!')


def main():
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
