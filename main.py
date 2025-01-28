import sys
import pymysql
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel, \
    QTableWidget, QTableWidgetItem, QDialog, QMessageBox, QComboBox
import config  # Импортируем конфигурацию


# Подключение к базе данных MySQL через PyMySQL с использованием конфигурации из config.py
def connect_db():
    try:
        print("Подключаемся к базе данных...")  # Для дебага
        db_config = config.DB_CONFIG  # Получаем настройки подключения
        return pymysql.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database'],
            charset=db_config['charset']
        )
    except pymysql.MySQLError as e:
        print(f"Ошибка при подключении к базе данных: {e}")  # Для дебага
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
        print("Полученные огнетушители:", extinguishers)  # Выводим для диагностики
        return extinguishers
    except pymysql.MySQLError as e:
        print(f"Ошибка при выполнении запроса: {e}")
        return []
    finally:
        conn.close()



# Получение данных о корпусах
def get_corps():
    print("Получаем данные о корпусах...")  # Для дебага
    conn = connect_db()
    if not conn:
        return []  # Если соединение не удалось, возвращаем пустой список

    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM corps")
        corps = cursor.fetchall()
        print(f"Полученные корпусы: {corps}")  # Для дебага
        return corps
    except pymysql.MySQLError as e:
        print(f"Ошибка при выполнении запроса: {e}")  # Для дебага
        return []
    finally:
        conn.close()


# Получение данных о корпусе по его ID
def get_corps_by_id(corp_id):
    conn = connect_db()
    if not conn:
        return None  # Если соединение не удалось, возвращаем None

    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM corps WHERE id = %s", (corp_id,))
        corp = cursor.fetchone()
        return corp  # Возвращаем данные корпуса
    except pymysql.MySQLError as e:
        print(f"Ошибка при выполнении запроса: {e}")
        return None
    finally:
        conn.close()


# Добавление нового огнетушителя в базу данных
def add_fire_extinguisher(number, cabinet, expiration_date, needs_replacement, corp_id):
    conn = connect_db()
    if not conn:
        print("Ошибка подключения к базе данных!")
        return  # Если соединение не удалось, прерываем выполнение функции

    cursor = conn.cursor()
    try:
        cursor.execute(""" 
            INSERT INTO fire_extinguishers (number, cabinet, expiration_date, needs_replacement, corp_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (number, cabinet, expiration_date, needs_replacement, corp_id))
        conn.commit()
    except pymysql.MySQLError as e:
        print(f"Ошибка при выполнении запроса: {e}")
    finally:
        conn.close()


# Добавление нового корпуса
def add_corp(number, address):
    conn = connect_db()
    if not conn:
        print("Ошибка подключения к базе данных!")
        return  # Если соединение не удалось, прерываем выполнение функции

    cursor = conn.cursor()
    try:
        cursor.execute(""" 
            INSERT INTO corps (number, address)
            VALUES (%s, %s)
        """, (number, address))
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
        self.setGeometry(150, 150, 1500, 750)

        # Устанавливаем цвет фона всего окна
        self.setStyleSheet("background-color: gray;")  # Задний фон всего окна в черный

        layout = QVBoxLayout()

        # Кнопка для отображения огнетушителей
        self.fire_extinguishers_button = QPushButton('Все огнетушители', self)
        self.fire_extinguishers_button.setEnabled(False)  # Изначально кнопка неактивна
        self.fire_extinguishers_button.clicked.connect(self.show_fire_extinguishers)
        self.fire_extinguishers_button.setStyleSheet(
            "background-color: #BDFF00; color: black; border-radius: 5px; font-family: 'SF Pro'; font-size: 25px;")  # Стиль кнопки
        layout.addWidget(self.fire_extinguishers_button)

        # Кнопка для добавления огнетушителей (только для администратора)
        if self.user[3] == 'admin':
            self.add_extinguisher_button = QPushButton('Добавить огнетушитель', self)
            self.add_extinguisher_button.clicked.connect(self.add_fire_extinguisher)
            self.add_extinguisher_button.setStyleSheet(
                "background-color: #BDFF00; color: black; border-radius: 5px; font-family: 'SF Pro'; font-size: 25px;")  # Стиль кнопки
            layout.addWidget(self.add_extinguisher_button)

            # Кнопка для добавления корпуса
            self.add_corp_button = QPushButton('Добавить корпус', self)
            self.add_corp_button.clicked.connect(self.add_corp)
            self.add_corp_button.setStyleSheet(
                "background-color: #BDFF00; color: black; border-radius: 25; font-family: 'SF Pro'; font-size: 25px;")  # Стиль кнопки
            layout.addWidget(self.add_corp_button)

        # Кнопка для выхода из программы
        self.logout_button = QPushButton('Выход', self)
        self.logout_button.clicked.connect(self.close)
        self.logout_button.setStyleSheet(
            "background-color: #BDFF00; color: black; border-radius: 25px; font-family: 'SF Pro'; font-size: 25px;")  # Стиль кнопки
        layout.addWidget(self.logout_button)

        self.setLayout(layout)

        # После авторизации активируем кнопку "Все огнетушители"
        self.fire_extinguishers_button.setEnabled(True)


    def show_fire_extinguishers(self):
        # Получаем данные о огнетушителях
        extinguishers = get_fire_extinguishers()
        print(f"Полученные огнетушители: {extinguishers}")  # Для дебага
        if not extinguishers:
            QMessageBox.warning(self, 'Ошибка', 'Не удалось загрузить данные об огнетушителях!')
            return

        # Создаем таблицу для отображения
        table = QTableWidget()
        table.setRowCount(len(extinguishers))
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(['Номер', 'Кабинет', 'Годен до', 'Требуется замена', 'Корпус'])

        # Заполняем таблицу данными
        for i, ext in enumerate(extinguishers):
            ext_id, number, cabinet, expiration_date, needs_replacement, corp_id = ext

            table.setItem(i, 0, QTableWidgetItem(str(number)))  # Номер огнетушителя
            table.setItem(i, 1, QTableWidgetItem(str(cabinet)))  # Кабинет
            table.setItem(i, 2, QTableWidgetItem(str(expiration_date)))  # Годен до (дата)
            table.setItem(i, 3, QTableWidgetItem('Да' if needs_replacement else 'Нет'))  # Требуется замена

            # Получаем данные корпуса по ID
            corp_name = get_corps_by_id(corp_id)
            if corp_name:
                table.setItem(i, 4, QTableWidgetItem(corp_name[1]))  # Адрес корпуса
            else:
                table.setItem(i, 4, QTableWidgetItem('Не найдено'))  # Если корпус не найден

        # Создаем диалоговое окно для отображения таблицы
        dialog = QDialog(self)
        dialog.setWindowTitle("Все огнетушители")
        dialog.setGeometry(150, 150, 1500, 750)  # Устанавливаем размеры окна

        layout = QVBoxLayout()
        layout.addWidget(table)
        dialog.setLayout(layout)

        # Пытаемся показать диалог с таблицей
        try:
            dialog.exec_()  # Это модальное окно, которое блокирует остальную часть интерфейса
            print("Диалог с таблицей успешно отображен.")  # Для дебага
        except Exception as e:
            print(f"Ошибка при отображении диалога с таблицей: {e}")  # Для дебага

    def add_fire_extinguisher(self):
        print("Открываем диалог для добавления огнетушителя...")  # Для дебага
        dialog = AddFireExtinguisherDialog(self)
        dialog.exec_()
        print("Диалог для добавления огнетушителя закрыт.")  # Для дебага

    def add_corp(self):
        print("Открываем диалог для добавления корпуса...")  # Для дебага
        dialog = AddCorpDialog(self)
        dialog.exec_()
        print("Диалог для добавления корпуса закрыт.")  # Для дебага


class AddFireExtinguisherDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Добавить огнетушитель")
        self.setGeometry(750, 350, 400, 300)

        layout = QVBoxLayout()

        # Используем ранее определенные цвета
        self.button_bg_color = "#BDFF00"
        self.button_text_color = "black"
        self.button_border_radius = "5px"
        self.font_family = "'SF Pro'"
        self.font_size = "14px"

        # Цвет фона для текстовых полей (можно легко изменить в коде)
        self.input_bg_color = "lightgray"  # Цвет фона для всех полей ввода

        # Поля ввода и метки
        self.number_label = QLabel('Номер огнетушителя:', self)
        self.number_input = QLineEdit(self)
        self.number_input.setStyleSheet(f"background-color: {self.input_bg_color}; font-family: {self.font_family}; font-size: {self.font_size};")
        layout.addWidget(self.number_label)
        layout.addWidget(self.number_input)

        self.cabinet_label = QLabel('Кабинет:', self)
        self.cabinet_input = QLineEdit(self)
        self.cabinet_input.setStyleSheet(f"background-color: {self.input_bg_color}; font-family: {self.font_family}; font-size: {self.font_size};")
        layout.addWidget(self.cabinet_label)
        layout.addWidget(self.cabinet_input)

        self.expiration_label = QLabel('Годен до (ГГГГ-ММ-ДД):', self)
        self.expiration_input = QLineEdit(self)
        self.expiration_input.setStyleSheet(f"background-color: {self.input_bg_color}; font-family: {self.font_family}; font-size: {self.font_size};")
        layout.addWidget(self.expiration_label)
        layout.addWidget(self.expiration_input)

        self.replacement_label = QLabel('Требуется замена:', self)
        self.replacement_button_yes = QPushButton('Да', self)
        self.replacement_button_yes.setStyleSheet(
            f"background-color: lightgreen; font-family: {self.font_family}; font-size: {self.font_size};")
        self.replacement_button_yes.clicked.connect(self.set_replacement_yes)

        self.replacement_button_no = QPushButton('Нет', self)
        self.replacement_button_no.setStyleSheet(
            f"background-color: lightcoral; font-family: {self.font_family}; font-size: {self.font_size};")
        self.replacement_button_no.clicked.connect(self.set_replacement_no)

        layout.addWidget(self.replacement_label)
        layout.addWidget(self.replacement_button_yes)
        layout.addWidget(self.replacement_button_no)

        # Выпадающий список для выбора корпуса
        self.corp_label = QLabel('Выберите корпус:', self)
        self.corp_combo = QComboBox(self)
        self.load_corps()
        self.corp_combo.setStyleSheet(
            f"background-color: {self.input_bg_color}; font-family: {self.font_family}; font-size: {self.font_size};")
        layout.addWidget(self.corp_label)
        layout.addWidget(self.corp_combo)

        self.save_button = QPushButton('Сохранить', self)
        self.save_button.setStyleSheet(
            f"background-color: {self.button_bg_color}; color: {self.button_text_color}; "
            f"border-radius: {self.button_border_radius}; font-family: {self.font_family}; font-size: {self.font_size};")
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
        corp_id = self.corp_combo.currentData()

        # Сохраняем данные в базу данных
        add_fire_extinguisher(number, cabinet, expiration_date, self.needs_replacement, corp_id)

        QMessageBox.information(self, 'Успех', 'Огнетушитель добавлен!')
        self.close()

    def load_corps(self):
        corps = get_corps()
        for corp in corps:
            # Добавляем строку "Номер корпуса - Адрес"
            corp_name = f"{corp[1]} - {corp[2]}"
            self.corp_combo.addItem(corp_name, corp[0])  # Добавляем имя и ID корпуса в комбинированный список


class AddCorpDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Добавить корпус")
        self.setGeometry(750, 350, 400, 200)

        layout = QVBoxLayout()

        self.number_label = QLabel('Номер корпуса:', self)
        self.number_input = QLineEdit(self)
        layout.addWidget(self.number_label)
        layout.addWidget(self.number_input)

        self.address_label = QLabel('Адрес корпуса:', self)
        self.address_input = QLineEdit(self)
        layout.addWidget(self.address_label)
        layout.addWidget(self.address_input)

        self.save_button = QPushButton('Сохранить', self)
        self.save_button.clicked.connect(self.save_corp)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def save_corp(self):
        number = self.number_input.text()
        address = self.address_input.text()

        # Сохраняем данные в базу данных
        add_corp(number, address)

        QMessageBox.information(self, 'Успех', 'Корпус добавлен!')
        self.close()


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Авторизация")
        self.setGeometry(750, 350, 400, 250)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Устанавливаем цвет фона всего окна
        self.setStyleSheet("background-color: black;")  # Задний фон всего окна в ярко-зеленый

        # Создаем и настраиваем элементы
        self.username_label = QLabel('Имя пользователя:', self)
        self.username_input = QLineEdit(self)
        self.username_label.setStyleSheet("color: #BDFF00; font-family: 'SF Pro'; font-size: 14px;")  # Цвет текста
        self.username_input.setStyleSheet(
            "background-color: gray; border: 1px solid gray; font-family: 'SF Pro'; font-size: 14px;")  # Шрифт и размер

        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)

        self.password_label = QLabel('Пароль:', self)
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_label.setStyleSheet("color: #BDFF00; font-family: 'SF Pro'; font-size: 14px;")  # Цвет текста
        self.password_input.setStyleSheet(
            "background-color: gray; border: 1px solid gray; font-family: 'SF Pro'; font-size: 14px;")

        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)

        self.login_button = QPushButton('Войти', self)
        self.login_button.clicked.connect(self.login)
        self.login_button.setStyleSheet(
            "background-color: #BDFF00; color: black; border-radius: 5px; font-family: 'SF Pro'; font-size: 14px;")  # Шрифт и размер для кнопки

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
            QMessageBox.warning(self, 'Ошибка', 'Неверное имя пользователя или пароль!')


def main():
    app = QApplication(sys.argv)

    login_window = LoginWindow()
    login_window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
