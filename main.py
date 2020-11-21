import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget
import sqlite3


# Наследуемся от виджета из PyQt5.QtWidgets и от класса с интерфейсом
class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.load_table()
        self.AddButton.clicked.connect(self.add)
        self.EditButton.clicked.connect(self.edit)

    def load_table(self):
        con = sqlite3.connect('coffee.sqlite')
        cur = con.cursor()
        lest = cur.execute('select * from coffee').fetchall()
        bar = cur.execute('pragma table_info(coffee)').fetchall()
        for i in range(len(bar)):
            bar[i] = bar[i][1]
        self.tableWidget.setColumnCount(len(bar))
        self.tableWidget.setRowCount(len(lest))
        self.tableWidget.setHorizontalHeaderLabels(bar)
        for i, elem in enumerate(lest):
            for j, val in enumerate(elem):
                self.tableWidget.setItem(i, j, QtWidgets.QTableWidgetItem(str(val)))
        for i in range(7):
            self.tableWidget.setColumnWidth(i, self.tableWidget.width() / 7.05)
        con.close()

    def add(self):
        addForm = addEditCoffeeForm(self)
        addForm.load_combo_box()

    def edit(self):
        con = sqlite3.connect('coffee.sqlite')
        cur = con.cursor()
        editForm = addEditCoffeeForm(self)
        editForm.NameLineEdit.setText(self.tableWidget.item(self.tableWidget.currentRow(), 1).text())
        grade = cur.execute('select name from grade_of_coffee where id = ?',(self.tableWidget.item(self.tableWidget.currentRow(), 2).text(),)).fetchone()[0]
        con.close()
        editForm.GradeComboBox.addItem(grade)
        editForm.StatusSpinBox.setValue(int(self.tableWidget.item(self.tableWidget.currentRow(), 3).text()))
        editForm.DescriptionLineEdit.setText(self.tableWidget.item(self.tableWidget.currentRow(), 4).text())
        editForm.PriceLineEdit.setText(self.tableWidget.item(self.tableWidget.currentRow(), 5).text())
        editForm.VolumeLineEdit.setText(self.tableWidget.item(self.tableWidget.currentRow(), 6).text())
        editForm.id = int(self.tableWidget.item(self.tableWidget.currentRow(), 0).text())
        editForm.load_combo_box()


class addEditCoffeeForm(QWidget):
    def __init__(self, parent):
        super(addEditCoffeeForm,self).__init__(parent)
        self.parent = parent
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Window)
        uic.loadUi('addEditCoffeeForm.ui', self)
        self.show()
        self.id = None
        self.SaveButton.clicked.connect(self.save)


    def save(self):
        cool = False
        self.ErrorLabel.setText('')
        try:
            self.price = int(self.PriceLineEdit.text())
            if self.PriceLineEdit.text() == '':
                raise BaseException
            cool = True
        except BaseException:
            self.ErrorLabel.setText('Укажите цену целым числом')
        try:
            self.volume = int(self.VolumeLineEdit.text())
            if self.VolumeLineEdit.text() == '':
                raise BaseException
            cool = True
        except BaseException:
            cool = False
            self.ErrorLabel.setText('Укажите объем целым числом')
        if cool:
            if self.id is None:
                self.do_add()
            else:
                self.do_edit()

    def do_add(self):
        con = sqlite3.connect('coffee.sqlite')
        cur = con.cursor()
        self.name = self.NameLineEdit.text()
        self.grade = cur.execute('select id from grade_of_coffee where name = ?', (self.GradeComboBox.currentText(),)).fetchall()[0][0]
        try:
            self.id = cur.execute('select id from coffee').fetchall()[-1][0] + 1
        except BaseException:
            self.id = 0
        self.status = self.StatusSpinBox.value()
        self.description = self.DescriptionLineEdit.text()
        done = (self.id, self.name, self.grade, self.status, self.description, self.price, self.volume)
        exec = 'insert into coffee(id,name,grade,status,description,price,volume) values(?,?,?,?,?,?,?)'
        cur.execute(exec,done)
        con.commit()
        con.close()
        self.parent.load_table()
        self.close()

    def do_edit(self):
        con = sqlite3.connect('coffee.sqlite')
        cur = con.cursor()
        self.name = self.NameLineEdit.text()
        self.grade = cur.execute('select id from grade_of_coffee where name = ?', (self.GradeComboBox.currentText(),)).fetchall()[0][0]
        self.status = self.StatusSpinBox.value()
        self.description = self.DescriptionLineEdit.text()
        exec = 'UPDATE coffee set name = ? where id = ?'
        cur.execute(exec,(self.name,self.id))
        exec = 'UPDATE coffee set grade = ? where id = ?'
        cur.execute(exec, (self.grade, self.id))
        exec = 'UPDATE coffee set status = ? where id = ?'
        cur.execute(exec, (self.status, self.id))
        exec = 'UPDATE coffee set description = ? where id = ?'
        cur.execute(exec, (self.description, self.id))
        exec = 'UPDATE coffee set price = ? where id = ?'
        cur.execute(exec, (self.volume, self.id))
        exec = 'UPDATE coffee set volume = ? where id = ?'
        cur.execute(exec, (self.volume, self.id))
        con.commit()
        con.close()
        self.parent.load_table()
        self.close()

    def load_combo_box(self):
        con = sqlite3.connect('coffee.sqlite')
        cur = con.cursor()
        grade = list(map(lambda x: x[0],cur.execute('select name from grade_of_coffee').fetchall()))
        if self.GradeComboBox.currentText() in grade:
            grade.remove(self.GradeComboBox.currentText())
        for i in grade:
            self.GradeComboBox.addItem(i)
        con.close()

def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())