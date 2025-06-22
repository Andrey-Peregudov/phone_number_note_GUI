from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QTextEdit, QLineEdit
from PyQt5 import uic
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
import sys
import os
from model.database import Database
from model.models import UserDB
from sqlalchemy import select
import asyncio

class DataBaseWorker(QThread):
    data_loaded = pyqtSignal(list)

    def __init__(self, database):
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

    def add_user(self, first_name, last_name, phone_nuber):
        try:
            asyncio.run(self.add_entry_to_db_sync(first_name, last_name, phone_nuber))
        except Exception as e:
            print(f"Ошибка при вызове add_entry_to_db_sync: {e}")

    async def add_entry_to_db_sync(self, first_name: str, last_name: str, phone_nuber: str):
        try:
            async for session in self.database.get_session():
                entry = UserDB(first_name=first_name, last_name=last_name, number=phone_nuber)
                session.add(entry)
                await session.commit()
                print(f"Запись успешно добавлена: {first_name} {last_name} {phone_nuber}")
                break  # Важно: выходим из цикла после успешной записи
        except Exception as e:
            print(f"Ошибка при добавлении записи в БД: {e}")


class Ui(QMainWindow):
    def __init__(self, database):
        super(Ui, self).__init__()
        self.database = database  # Теперь это экземпляр класса, а не класс
        try:
            # Подключение интерфейса
            uic.loadUi('tel_numb.ui', self)
            self.setWindowTitle("Телефонный справочник")
            self.show()

            self.firstName = self.findChild(QLineEdit, "textFirstname")
            self.lastName = self.findChild(QLineEdit, "textLastname")
            self.phoneNuber = self.findChild(QLineEdit, "textNumber")

            self.addButton = self.findChild(QPushButton, "pushButton")
            if self.addButton:
                self.addButton.clicked.connect(self.entry_phone_book)
                print("Сигнал clicked подключен к entry_phone_book")
            else:
                print("Ошибка: Кнопка с именем pushButton не найдена")

            self.database_worker = DataBaseWorker(self.database)
            self.database_worker.start()

            #self.entry_phone_book()  # Убираем вызов здесь

        except FileNotFoundError:
            # Исключение если файл с пользовательским интерфесом не найден
            print("Ошибка: Файл не найден")
            sys.exit(1)
        except Exception as e:
            # Прочие ошибки при запуске
            print(f"Ошибка при запуске {e}")
            sys.exit(1)

    # def exist_file(self):
    #     try:
    #         if os.path.exists("database.db"):
    #             print("Файл существует")
    #         else:
    #             # Используем синхронный вызов создания таблиц
    #             self.create_db_and_tables_sync()
    #             print("Такого файла нет")
    #     except Exception as e:
    #         print(f"Ошибка {e}")

    # def create_db_and_tables_sync(self):
    #     """Синхронная функция для создания базы данных и таблиц."""
    #     for session in self.database.get_session():
    #         self.database.create_db_and_tables()
    #         session.commit()
    #         break  # Выходим из цикла после успешного создания

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

        self.database_worker.add_user(first_name, last_name, phone_nuber)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    database = Database()  # Создаем экземпляр Database
    window = Ui(database)  # Передаем экземпляр Database

    #Создание файла при старте
    #import asyncio #Не нужно здесь
    #async def create_tables():
    #    await database.create_db_and_tables()
    #asyncio.run(create_tables())

    sys.exit(app.exec_())