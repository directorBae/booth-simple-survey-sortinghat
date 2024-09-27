import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QStackedWidget, QMessageBox
from PyQt5.QtGui import QFont, QPixmap, QPalette, QBrush
from PyQt5.QtCore import Qt
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl
import time

import win32print
import win32ui
import win32con
import os
from PIL import Image, ImageWin

pnglist = ["Gryffindor.png", "Hufflepuff.png", "Ravenclaw.png", "Slytherin.png"]

class PrintFile():
    def __init__(self):
        self.pnglist = ["Gryffindor.png", "Hufflepuff.png", "Ravenclaw.png", "Slytherin.png"]
    
    def printFile(self, file_path):
        if not file_path in self.pnglist:
            print(f"Invalid file: {file_path}")
            return
        try:
            printer_name = win32print.GetDefaultPrinter()

            # Open the printer and get its info
            hprinter = win32print.OpenPrinter(printer_name)
            printer_info = win32print.GetPrinter(hprinter, 2)

            # Create a Device Context for the printer
            pdc = win32ui.CreateDC()
            pdc.CreatePrinterDC(printer_info['pPrinterName'])

            # Start the document and page for printing
            pdc.StartDoc(file_path)
            pdc.StartPage()

            # Open the image file and adjust its size to fit the printer's resolution
            image = Image.open(file_path)
            
            n = 2  # 이미지 크기를 1/n 으로 조절하려면 n 값을 조절하세요.
            new_width = image.size[0] // n
            new_height = image.size[1] // n
            image = image.resize((new_width, new_height)) 

            if image.size[1] > image.size[0]:
                image = image.rotate(90, expand=True)

            hsize = int((float(image.size[1]) * float(pdc.GetDeviceCaps(win32con.HORZRES))) / float(image.size[0]))
            vsize = int((float(image.size[0]) * float(pdc.GetDeviceCaps(win32con.VERTRES))) / float(image.size[1]))
            image = image.resize((vsize // n, hsize // n))

            # Draw the image to the Device Context
            dib = ImageWin.Dib(image)
            dib.draw(pdc.GetHandleOutput(), (0, 0, pdc.GetDeviceCaps(win32con.HORZRES), hsize))

            # End the page and document
            pdc.EndPage()
            pdc.EndDoc()

            # Delete the Device Context
            pdc.DeleteDC()
        
        except Exception as e:
            print(f"Failed to print {file_path}: {e}")

class SurveyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.printer = PrintFile()  # 프린트 관련 클래스 (구현되어 있다고 가정)
        self.showFullScreen()

        # QMediaPlayer 설정 (음악 재생)
        self.player = QMediaPlayer()
        media_url = QUrl.fromLocalFile("HedwigsTheme.mp3")  # 음악 파일 경로
        self.player.setMedia(QMediaContent(media_url))
        self.player.setVolume(70)  # 볼륨 설정

        # 음성 재생 파일 설정
        self.voices = ["voice/intro.wav", "voice/q1.wav", "voice/q2.wav", "voice/q3.wav", "voice/q4.wav", "voice/그리핀도르.wav", "voice/후플푸프.wav", "voice/래번클로.wav", "voice/슬리데린.wav"]
        self.voice_player = QMediaPlayer()
        self.voice_player.setVolume(100)
        media_url = QUrl.fromLocalFile(self.voices[0])
        self.voice_player.setMedia(QMediaContent(media_url))

        # 폰트 설정
        self.setFont(QFont('Pretendard', 12))

        # 배경 이미지 설정
        self.set_background_image("main.png")  # main.png 이미지를 배경으로 설정

        # QLabel 및 QPushButton 스타일 설정
        self.setStyleSheet("""
            QLabel {
                font-family: Pretendard;
                font-size: 36px;
                font-weight: bold;
                color: #FFFFFF;
                margin-bottom: 20px;
            }       
            QPushButton {
                font-family: Pretendard;
                background-color: #FFFFFF50;
                color: black;
                width: 300px;

                border: none;
                padding: 15px 20px;
                font-size: 14px;
                border-radius: 10px;
                margin: 5px 0;
            }
            QPushButton:hover {
                color: #fff200;
            }
        """)

        self.questions = [
            "오늘, 중요한 시험에 늦잠을 잤다면?",
            "가막못에 물고기가 하나 산다면...",
            "신입생이 된 당신에게 선배가 건네는 첫 인사는?",
            "교수님이 찾아와 자기 랩으로 오라고 한다. 내 첫 마디는?"
        ]

        self.options = [
            ["침착하게 인스타에 올린다", "가막못으로 달려간다"],
            ["낚시한다", "함께 수영한다"],
            ["나한테 인사를 할 리가 없다", "딸기당근수박참외...론메?"],
            ["교수님의 개가 되어 충성을 다하겠습니다!", "문의는 DM으로 부탁드려요."],
        ]

        self.responses = [None] * len(self.questions)

        # Stacked widget to handle start page and survey
        self.stacked_widget = QStackedWidget(self)

        # Create the start page
        self.start_page = self.create_start_page()
        self.stacked_widget.addWidget(self.start_page)

        # Create pages for each question
        self.pages = []
        for i in range(len(self.questions)):
            page = self.create_question_page(i)
            self.pages.append(page)
            self.stacked_widget.addWidget(page)

        # Add stacked widget to the main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.stacked_widget)
        self.setLayout(main_layout)

    def set_background_image(self, image_path):
        """배경 이미지를 창 크기에 맞게 설정하는 메서드"""
        palette = QPalette()

        # QPixmap으로 이미지를 로드한 후 창 크기에 맞춰 스케일 조정
        pixmap = QPixmap(image_path)

        # 창 크기에 맞춰 이미지 크기 조정
        scaled_pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)

        # QPalette에 이미지를 설정
        palette.setBrush(QPalette.Background, QBrush(scaled_pixmap))
        self.setPalette(palette)

    def create_start_page(self):
        """Create a start page with a start button."""
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)

        welcome_label = QLabel("해리 포터와 마법사의 못")
        welcome_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(welcome_label)

        start_button = QPushButton("모자 쓰기")
        start_button.clicked.connect(self.start_survey)
        layout.addWidget(start_button, alignment=Qt.AlignCenter)

        self.voice_player.stop()
        self.voice_player.setMedia(QMediaContent(QUrl.fromLocalFile(self.voices[0])))  # 시작 음성으로 이동
        self.voice_player.play()

        page.setLayout(layout)
        return page

    def start_survey(self):
        """Start the survey and begin music playback."""
        self.player.play()  # 음악 재생 시작
        self.voice_player.stop()
        self.voice_player.setMedia(QMediaContent(QUrl.fromLocalFile(self.voices[1])))  # 첫 번째 질문 음성으로 이동
        self.voice_player.play()
        self.stacked_widget.setCurrentIndex(1)  # 첫 번째 질문 페이지로 이동

    def create_question_page(self, question_index):
        """Create a page with a question and button options."""
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)  # 페이지 여백 설정
        layout.setSpacing(20)  # 위젯 간격 설정

        question_label = QLabel(self.questions[question_index])
        layout.addWidget(question_label, alignment=Qt.AlignCenter)

        # Create buttons for options
        for i, option in enumerate(self.options[question_index]):
            button = QPushButton(option)
            button.clicked.connect(self.handle_button_click(question_index, i))
            layout.addWidget(button, alignment=Qt.AlignCenter)

        page.setLayout(layout)
        return page

    def handle_button_click(self, question_index, option_index):
        """Store the selected answer for the given question and move to the next page."""
        def callback():
            self.responses[question_index] = option_index
            current_index = self.stacked_widget.currentIndex()
            if current_index + 1 < len(self.questions) + 1:
                self.stacked_widget.setCurrentIndex(current_index + 1)           
            else:
                house_index = self.determine_house()
                self.voice_player.stop()
                self.voice_player.setMedia(QMediaContent(QUrl.fromLocalFile(self.voices[house_index + 5])))  # 집결 결과 음성으로 이동
                self.voice_player.play()
                self.finish_survey()

            if question_index < 3:
                media_url = QUrl.fromLocalFile(self.voices[question_index + 2])  # 여기서 mp3 파일 경로를 지정하세요.
                self.voice_player.setMedia(QMediaContent(media_url))
                self.voice_player.play()
        return callback
    

    def determine_house(self):
        """Determine the house based on the survey responses."""
        total = 0
        print(self.responses)
        for i in range(len(self.responses)):
            total += int(self.responses[i]) * (2 ** i)
        house_index = total % 4
        return house_index

    def finish_survey(self):
        """Show a summary of the survey results and restart."""
        dorm_list = ["그리핀도르", "후플푸프", "래번클로", "슬리데린"]
        house_index = self.determine_house()
        house_name = dorm_list[house_index]
        
        QMessageBox.information(self, "", f"{house_name}에 온 걸 환영해!")

        self.player.stop()
        my_dorm = self.determine_house()
        print(f"Your house: {my_dorm}")
        # self.printer.printFile(self.printer.pnglist[my_dorm])
        self.voice_player.stop()
        self.voice_player.setMedia(QMediaContent(QUrl.fromLocalFile(self.voices[0])))  # 시작 음성으로 이동
        self.voice_player.play()
        self.reset_survey() 

    def reset_survey(self):
        """Reset the survey and go back to the start page."""
        # Reset responses
        self.responses = [None] * len(self.questions)

        # Go back to the start page
        self.stacked_widget.setCurrentIndex(0)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SurveyApp()
    window.show()
    sys.exit(app.exec_())
