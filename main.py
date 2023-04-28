import sys, googletrans
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QMenu, QAction, QMainWindow, QShortcut, QDesktopWidget
from googletrans import Translator #pip install googletrans==3.1.0a0
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QEvent
import locale
import json
from PyQt5.QtGui import QKeySequence, QClipboard, QGuiApplication, QPainter, QPainterPath, QRegion

class TranslatorThreat(QThread): # googletrans ile yapılan çeviri işlemini farklı bir threat üzerinden yapıyor
    counter_signal = pyqtSignal(str)
    
    def setData(self, translatedata, translatesource, translatedest): # ana threat üzerinden inputtext verisi buraya gönderiliyor
        self.translatedata = translatedata
        self.translatesource = translatesource
        self.translatedest= translatedest

    def run(self): # gelen veri çeviri fonksiyonuna sokuluyor

        translator = Translator()
        output = translator.translate(self.translatedata, dest=self.translatedest, src=self.translatesource)
        #print(output.extra_data)
        outputDict = {"src":output.src, "dest": output.dest, "text": output.text} #  çıktının içeriği Dict yapısına dönüştürülüyor
        outputStr= json.dumps(outputDict)
        self.counter_signal.emit(outputStr) # çeviri işlemi yapıldıktan sonra son veri main threat'e gönderiliyor
        

class PyTranslator(QWidget):
    def __init__(self):
        super().__init__()

        locale.setlocale(locale.LC_ALL, '') # sistem dilini algıla ('tr_TR', 'UTF-8')
        self.systemlang=locale.getlocale()[0].split("_")[0] # tr

        # Pencere özelliklerini ayarla
        self.setWindowTitle("Translator")
        screen = QDesktopWidget().screenGeometry() # ekran çözünürlüğü
        screenWidth, screenHeight = screen.width(), screen.height() # 1920,1080
        self.windowWidth, self.windowHeight = 750, 300
        Xcenter=(screenWidth - self.windowWidth) // 2
        Ycenter=(screenHeight - self.windowHeight) // 5 # tam ortası için 2'ye bölünecek
        self.setGeometry(Xcenter, Ycenter, self.windowWidth, self.windowHeight) # pencerenin konumunu ayarlıyor


        self.setStyleSheet("background-color: #fff; color:black;")

        #Kısayollar
        shortcut1 = QShortcut(QKeySequence("Ctrl+Q"), self)
        shortcut1.activated.connect(self.close_window)
        shortcut2 = QShortcut(QKeySequence("ESC"), self)
        shortcut2.activated.connect(self.close_window)
        shortcut3 = QShortcut(QKeySequence("Alt+C"), self)
        shortcut3.activated.connect(self.changeLangs)
        shortcut4 = QShortcut(QKeySequence("Alt+F"), self)
        shortcut4.activated.connect(self.focus_input)
        shortcut4 = QShortcut(QKeySequence("Alt+A"), self)
        shortcut4.activated.connect(self.set_auto)

       

        # İçerik widgetlarını ayarla
        self.input_text = QTextEdit()
        self.input_text.setStyleSheet("border:none; background:#E7E7E8; ")
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setStyleSheet("border:none; background:#E7E7E8; ")


        # Input alanındaki metin değiştiğinde output alanını güncelle
        self.input_text.textChanged.connect(self.start_translator) # input alanındaki veri değiştiğinde start_translator fonksiyonu tetikleniyor

        self.translator_thread = TranslatorThreat()
        self.translator_thread.counter_signal.connect(self.update_output_text) # çeviri işlemini yapan TranslatorThreat sınıfı sinyal gönderdiği zaman update_output_text fonksiyonu tetikleniyor
        # Buton widgetını ayarla
        self.button1 = QPushButton("auto")
        self.button1.setFixedWidth(100)
        self.button1.clicked.connect(self.show_menu1)

        self.changebutton = QPushButton("<->")
        self.changebutton.setFixedWidth(50)
        self.changebutton.clicked.connect(self.changeLangs)

        self.button2 = QPushButton(googletrans.LANGUAGES[self.systemlang])
        self.button2.setFixedWidth(100)
        self.button2.clicked.connect(self.show_menu2)


        # Menü widgetını ayarla
        self.menu1 = QMenu()

        action = QAction("auto", self)
        action.triggered.connect(lambda checked, text=action.text(): self.button1.setText(text))
        self.menu1.addAction(action)
        for value in googletrans.LANGUAGES.values():
            action = QAction(str(value), self)
            action.triggered.connect(lambda checked, text=action.text(): self.button1.setText(text))
            self.menu1.addAction(action)
            self.menu1.addSeparator()

        self.menu1.setFixedWidth(300)
        self.menu1.setFixedHeight(400)
        self.menu1.setStyleSheet("QMenu {}")
        
        self.menu2 = QMenu()
        for value in googletrans.LANGUAGES.values():
            action = QAction(str(value), self)
            action.triggered.connect(lambda checked, text=action.text(): self.start_translator(text))
            self.menu2.addAction(action)
            self.menu2.addSeparator()

        self.menu2.setFixedWidth(300)
        self.menu2.setFixedHeight(400)
        self.menu2.setStyleSheet("QMenu {}")

        self.logrecord=QTextEdit()
        self.logrecord.setReadOnly(True)
        self.logrecord.setFixedHeight(33)
        self.logrecord.setStyleSheet("border:none;")

        # Widgetları düzenle
        hbox1 = QHBoxLayout()
        hbox1.addWidget(self.input_text)
        hbox1.addWidget(self.output_text)

        hbox2 = QHBoxLayout()
        hbox2.addWidget(self.button1)
        hbox2.addWidget(self.changebutton)
        hbox2.addWidget(self.button2)

        hbox3 = QHBoxLayout()
        hbox3.addWidget(self.logrecord)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox3)

        self.setLayout(vbox)

        self.clipboard = QApplication.clipboard()
        if self.clipboard.mimeData().hasText():
            selected_text = self.clipboard.text()
            self.input_text.setText(selected_text)

        self.input_text.setFocus()
    def show_menu1(self):
        self.menu1.exec_(self.button1.mapToGlobal(self.button1.rect().bottomLeft()))


    def show_menu2(self):
        self.menu2.exec_(self.button2.mapToGlobal(self.button2.rect().bottomLeft()))

    def start_translator(self,text="empty"): # bu fonksiyon tetiklendiğinde farklı threat üzerindeki çeviriyi yapacak olan TranslatorThreat sınıfına input verisi gönderiliyor
        if text != "empty":
            self.button2.setText(text)
        source=self.button1.text()
        dest=self.button2.text()
        inputtext=self.input_text.toPlainText()
        if len(self.input_text.toPlainText()) > 0 : # input alanı boş ise çeviri fonksiyonu çalışmasın
            self.translator_thread.setData(inputtext,source,dest)
            self.translator_thread.start()
        else:
            self.output_text.setText("")
            self.logrecord.setText("Deleted")

    def update_output_text(self, outputStr): # çeviri işlemi yapıldığı zaman output alanı güncelleniyor
        # Input alanındaki metni output alanına kopyala
        self.outputDict = json.loads(outputStr)
        self.output_text.setText(self.outputDict['text'])
        logtext=googletrans.LANGUAGES[self.outputDict['src']] + " Algılandı"
        self.logrecord.setText(logtext)

    def changeLangs(self): # değiştir butonuna tıklandığında çalışacak fonksiyon
        if len(self.input_text.toPlainText()) > 0 : # text alanlarına bir metin girilmiş mi kontrol
            tmpdata = self.button1.text()
            self.button1.setText(self.button2.text()) # button1 butonunun yazısı button2 butonunun yazısı ile değiştiriliyor
            # button2 butonunun yazısı en son algılanmış dil ile değiştiriliyor
            if tmpdata == "auto":
                self.button2.setText(googletrans.LANGUAGES[self.outputDict['src']]) 
            else:
                self.button2.setText(tmpdata)
               
            
            inputtextTmp = self.input_text.toPlainText() # input alanındaki yazı geçici bir değişkene atanıyor
            self.input_text.setText(self.output_text.toPlainText()) # input alanına output alanındaki veri yazılıyor
            self.output_text.setText(inputtextTmp) # output alanına değişkene atadığımız input değişkeni yazılıyor
        elif self.button1.text() == "auto" :
            self.logrecord.setText("Source Lang is Auto")
        else :
            tmpdata=self.button1.text()
            self.button1.setText(self.button2.text())
            self.button2.setText(tmpdata)
            self.button1.text()
            

    def close_window(self):
        self.close()

    def focus_input(self):
        self.input_text.setFocus()
    def set_auto(self):
        self.button1.setText("auto")
        self.start_translator()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = PyTranslator()
    widget.setWindowFlag(Qt.FramelessWindowHint)
    # Pencere kenarlarını yuvarlaklaştır
    radius = 17
    path = QPainterPath()
    path.addRoundedRect(0,0,750,300, radius, radius)
    region = QRegion(path.toFillPolygon().toPolygon())
    widget.setMask(region)
    widget.show()
    sys.exit(app.exec_())
 
