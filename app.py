from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic
from PyQt5.QtCore import QThread, pyqtSignal
import sys
from .databese import Database
from .models import UserDB
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
        try:
            #Подключение интерфейса
            uic.loadUi('tel_numb.ui', self)
            self.setWindowTitle("Телефонный справочник")
            self.show()
        except FileNotFoundError:
            print("Ошибка: Файл не найден")
            sys.exit(1)
        except Exception as e:
            print(f"Ошибка при запуске {e}")
            sys.exit(1)

app = QApplication(sys.argv)

window = Ui()

app.exec_()