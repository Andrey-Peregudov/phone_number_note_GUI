from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QTextEdit, QLineEdit
from PyQt5 import uic
from PyQt5.QtCore import QThread, pyqtSignal
import sys
import os
from model.database import Database
from model.models import UserDB
from sqlalchemy import select

class DataBaseWorker(QThread):

    data_loaded = pyqtSignal(list)

    def __init__(self, database = Database):
        super().__init__()
        self.database = database

    async def load_users(self):
        async for session in self.database.get_session():
            result = await session.execute(select(UserDB))
            users = result.scalars().all()
            self.data_loaded.emit(users)  # Send list of users
            await session.commit()
            await session.close()
            print("Data fetched in thread")


class Ui(QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        self.database = Database
        try:
            #Подключение интерфейса
            uic.loadUi('tel_numb.ui', self)
            self.setWindowTitle("Телефонный справочник")
            self.show()
            self.exist_file()

            self.firstName = self.findChild(QLineEdit, "textFirstname")
            self.lastName = self.findChild(QLineEdit, "textLastname")
            self.phoneNuber = self.findChild(QLineEdit, "textNumber")

            self.addButton = self.findChild(QPushButton, "pushButton")
            if self.addButton:
                self.addButton.clicked.connect(self.entry_phone_book)
                print("Сигнал clicked подключен к entry_phone_book")
            else:
                print("Ошибка: Кнопка с именем pushButton не найдена")

            self.entry_phone_book()

        except FileNotFoundError:
            #Исключение если файл с пользовательским интерфесом не найден
            print("Ошибка: Файл не найден")
            sys.exit(1)
        except Exception as e:
            #Прочие ошибки при запуске
            print(f"Ошибка при запуске {e}")
            sys.exit(1)

    #Проверка наличие базы данных
    def exist_file(self):
        try:
            if os.path.exists("database.db"):
                print("Файл существует")
            else:
                import asyncio
                asyncio.run(self.database.create_db_and_tables())
                print("Такого файла нет")
        except Exception as e:
            print(f"Ошибка {e}")

    def entry_phone_book(self):
        first_name = self.firstName.text()
        last_name = self.lastName.text()
        phone_nuber = self.phoneNuber.text()

        try:
            if not first_name:
                print("Заполните имя")
                return
            if not last_name:
                print("Заполните фамилию")
                return
            if not phone_nuber:
                print("Заполните номер телефона")
                return
        except Exception as e:
            print(f"Ошибка {e}")

        QTimer.singleShot(0, lambda: asyncio.ensure_future(
            self.add_entry_to_db(first_name, last_name, phone_nuber)))  # Оставляем как есть

    def add_entry_to_db(self, first_name: str, last_name: str,
                              phone_nuber: str):  # phone_nuber оставляем как есть
        # Функция для добавления данных
        try:
            for session in self.database.get_session():
                entry = UserDB(first_name=first_name, last_name=last_name,
                               number=phone_nuber)  # number - как называется поле в БД
                session.add(entry)
                session.commit()
                print(f"Запись успешно добавлена: {first_name} {last_name} {phone_nuber}")  # phone_nuber - как есть
        except Exception as e:
            print(f"Ошибка при добавлении записи в БД: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    database = Database()
    window = Ui()
    # Создание файла при старте
    import asyncio
    async def create_tables():
        await database.create_db_and_tables()
    asyncio.run(create_tables())
    sys.exit(app.exec_())