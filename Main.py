import json
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QLabel, QHBoxLayout, QPushButton, QScrollArea
from PyQt6.QtGui import QPainter, QColor

CodesLUT = {
    "A" : "0000000011100000001100011000110000000110000000110",
    "E" : "0000000000000000001100011000110000000000000000000",
    "I" : "0000000000000011000000011000000011000000000000000",
    "O" : "0000100011110010010000110100000010000010000010000",
    "U" : "0001000001000001000001111110000010001010000010000",
    "M" : "0000000000000011111101000000010000001000000000000",
    "N" : "0100000011000001011000100000010000001000001000000",
    "P" : "0000000000000001111100100001010000111100100000000",
    "T" : "0000000000000001111001000010000001000111000000000",
    "K" : "0000000000000011111100000100000100000100000000000",
    "S" : "0010000001000000100000010000001000001000001000000",
    "C" : "1000000100000010010001010000110000010000001000000",
    "F" : "0000000001000000110000010100101000001100000010000",
    "D" : "0000000000000001111100000100000100011111110000000",
    "H" : "0001000000100000010000001000110100000110000000110",
    "R" : "0010000011100010101000010000001000000100000010000",
    "L" : "0000000000100000100000100000110000000110000000110",
    "V" : "0100000011000001011000100000011000001011001000000",
    "W" : "0100100011011001011010100100011010001011001000100",
    "X" : "0111100000100000100001111110000010001010000010000",
    "Y" : "0110000100101000111000110000000100010010000110000",
    "Z" : "0010000001000011111100010100001100001100000010000",
    "1" : "0000000111111000000000000000000000000000000000000",
    "2" : "0000000111111000000100000010000000000000000000000",
    "3" : "1111110000001000000101111110000000000000000000000",
    "4" : "1111110000001000000101111110000001000000100000000",
    "5" : "1000000100000010000001100000101100010001100000000",
    "6" : "1001110100000010000001100000101100010001100000000",
    "7" : "1001110100001010000001100000101100010001100000000",
    "8" : "1001110100001010011101100000101100010001100000000",
    "9" : "1001110100001010011101100010101100010001100000000",
    "0" : "1110000001001000000101111110000000000000000000000",
    " " : "0000000000000000000000000000000000000000000000000"
}

class Word:
    def __init__(self, Roman, Translation = None):
        self.Roman = Roman.upper()
        self.Translation = Translation

class Dict:
    WordList = []

    def AddWord(Roman, Translation = None):
        Match = False
        for word in Dict.WordList:
            if word.Roman == Roman:
                Match = True
        if not Match:
            Dict.WordList.append(Word(Roman, Translation))
    
    def SaveDict():
        json.encoder(Dict.WordList)


    def LoadDict():
        pass

class GlyphWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.text = ""
        self.pixel_size = 1   
        self.glyph_size = 7   

    def setText(self, text):
        self.text = text.upper()
        self.update()  

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 0))

        x_offset = 10
        y_offset = 10

        for char in self.text:
            if char not in CodesLUT:
                x_offset += self.glyph_size * self.pixel_size
                continue

            code = CodesLUT[char]

            for i, bit in enumerate(code):
                if bit == "1":
                    x = i % self.glyph_size
                    y = i // self.glyph_size

                    painter.fillRect(
                        x_offset + x * self.pixel_size,
                        y_offset + y * self.pixel_size,
                        self.pixel_size,
                        self.pixel_size,
                        QColor(255, 255, 255),
                    )

            x_offset += (self.glyph_size + 1) * self.pixel_size

class AddWordWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window

        self.setWindowTitle("Add Word")

        layout = QVBoxLayout()

        self.roman_input = QLineEdit()
        self.roman_input.setText(self.main_window.input.text())
        self.roman_input.setPlaceholderText("Roman text")
        layout.addWidget(self.roman_input)

        self.translation_input = QLineEdit()
        self.translation_input.setPlaceholderText("Translation")
        layout.addWidget(self.translation_input)

        self.preview = GlyphWidget()
        self.preview.setMinimumHeight(50)
        layout.addWidget(self.preview)

        self.roman_input.textChanged.connect(self.preview.setText)

        self.add_btn = QPushButton("Add")
        self.add_btn.clicked.connect(self.add_word)
        layout.addWidget(self.add_btn)

        self.setLayout(layout)

    def add_word(self):
        roman = self.roman_input.text()
        translation = self.translation_input.text()

        if roman:
            Dict.AddWord(roman, translation)
            self.main_window.update_dict()
            self.close()

class EditWindow(QWidget):
    def __init__(self, word, window):
        super().__init__()

        self.word = word
        self.window = window

        self.setWindowTitle(f"Edit: {word.Roman}")

        layout = QVBoxLayout()

        self.input = QLineEdit()
        self.input.setText(word.Translation if word.Translation else "")
        layout.addWidget(self.input)

        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save)
        layout.addWidget(self.save_btn)

        self.setLayout(layout)

    def save(self):
        self.word.Translation = self.input.text()
        self.window.update_dict()
        self.close()

class MainWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Fruman Dictionary")

        self.layout = QVBoxLayout()
        top_layout = QHBoxLayout()


        self.input = QLineEdit()
        self.input.setPlaceholderText("Type here...")
        top_layout.addWidget(self.input)

        self.add_btn = QPushButton("Add Word")
        self.add_btn.clicked.connect(self.open_add_window)
        top_layout.addWidget(self.add_btn)

        self.layout.addLayout(top_layout)

        self.display = GlyphWidget()
        self.display.setMinimumHeight(25)
        self.layout.addWidget(self.display)

        self.dict_view = DictView(Dict.WordList, self)
        self.layout.addWidget(self.dict_view)

        self.setLayout(self.layout)

        self.input.textChanged.connect(self.display.setText)
        self.input.textChanged.connect(self.update_dict)
    
    def update_dict(self):
        self.layout.removeWidget(self.dict_view)
        self.dict_view = DictView(Dict.WordList, self)
        self.layout.addWidget(self.dict_view)

    def open_add_window(self):
        self.add_window = AddWordWindow(self)
        self.add_window.show()

class WordRow(QWidget):
    def __init__(self, word, window):
        super().__init__()
        self.window = window
        layout = QHBoxLayout()
        self.word = word
        self.glyph = GlyphWidget()
        self.glyph.setText(word.Roman)
        self.glyph.setFixedHeight(25)
        self.glyph.setMinimumWidth(len(word.Roman)*9)

        self.roman = QLabel(word.Roman)
        self.roman.setMaximumWidth(200)

        translation_text = word.Translation if word.Translation else "-"
        self.translation = QLabel(translation_text)

        self.edit_btn = QPushButton("Edit Translation")
        self.edit_btn.clicked.connect(self.open_editor)

        self.del_btn = QPushButton("Remove Entry")
        self.del_btn.clicked.connect(self.Remove)


        layout.addWidget(self.glyph)
        layout.addWidget(self.roman)
        layout.addWidget(self.translation)
        layout.addWidget(self.edit_btn)
        layout.addWidget(self.del_btn)

        self.setLayout(layout)
    def open_editor(self):
        self.editor = EditWindow(self.word, self.window)
        self.editor.show()
    def Remove(self):
        Dict.WordList.remove(self.word)
        self.window.update_dict()

class DictView(QScrollArea):
    def __init__(self, word_list, window):
        super().__init__()

        container = QWidget()
        layout = QVBoxLayout()
        word_list.sort(key = self.DictSort)
        for word in word_list:
            if window.display.text == word.Roman[:len(window.display.text)]: 
                row = WordRow(word, window)
                layout.addWidget(row)

        container.setLayout(layout)
        self.setWidget(container)
        self.setWidgetResizable(True)
        layout.addStretch()

    def DictSort(self, Word):
        return Word.Roman

app = QApplication(sys.argv)
window = MainWindow()
window.resize(800, 300)
window.show()
sys.exit(app.exec())