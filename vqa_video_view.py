import json
import sys
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *
from PyQt5.QtWidgets import *
from os.path import basename
import os

class main(QMainWindow):
    json_list = []
    json_data = []
    current_index = 0

    def __init__(self, *args, **kwargs):
        super(main, self).__init__(*args, **kwargs)
        self.setWindowTitle("LabelOn 비디오내러티브 뷰어 Ver1.0")
        self.main_groupbox = QtWidgets.QGroupBox()
        self.setCentralWidget(self.main_groupbox)
        self.setWindowIcon(QtGui.QIcon('./icon/favicon-32x32.png'))
        self.main_layout = QtWidgets.QGridLayout(self.main_groupbox)

        menubar = self.menuBar()
        menu_folder_open = menubar.addMenu("파일")
        menu_open_folder = QAction("폴더열기", self)
        menu_open_folder.triggered.connect(self.open_folder)
        menu_exit_program = QAction("종료", self)
        menu_exit_program.triggered.connect(qApp.exit)
        menu_folder_open.addAction(menu_open_folder)
        menu_folder_open.addAction(menu_exit_program)

        self.playButton = QPushButton()
        self.playButton.setEnabled(False)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)

        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.video_widget = QVideoWidget()
        self.media_player.setVideoOutput(self.video_widget)
        self.positionSlider = QSlider(QtCore.Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)
        self.media_player.positionChanged.connect(self.positionChanged)
        self.media_player.durationChanged.connect(self.durationChanged)
        self.media_player.stateChanged.connect(self.mediaStateChanged)
        self.media_player.error.connect(self.handleError)
        self.errorLabel = QLabel()
        self.errorLabel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        self.video_group_box = QtWidgets.QGroupBox()
        self.video_layout = QtWidgets.QVBoxLayout(self.video_group_box)
        self.video_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.video_layout.addWidget(self.video_widget)
        self.video_layout.addWidget(self.playButton)
        self.video_layout.addWidget(self.positionSlider)
        self.video_layout.addWidget(self.errorLabel)

        self.qa_group_box = QtWidgets.QGroupBox()
        self.qa_layout = QtWidgets.QVBoxLayout(self.qa_group_box)
        self.qa_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        qa_detail_groupbox = QtWidgets.QGroupBox()
        qa_detail_groupbox.setFixedHeight(220)
        qa_detail_layout = QtWidgets.QGridLayout(qa_detail_groupbox)
        qa_label_question = QtWidgets.QLabel("질문 : ")
        qa_input_question = QtWidgets.QLineEdit()
        qa_input_question.setObjectName('question')
        qa_input_question.setReadOnly(True)
        qa_label_question.setMaximumWidth(100)

        qa_detail_layout.addWidget(qa_label_question, 0, 0, 1, 1)
        qa_detail_layout.addWidget(qa_input_question, 0, 1, 1, 1)
        for i in range(5):
            qa_label_answer = QtWidgets.QLabel("답변 {}: ".format(i+1))
            qa_label_answer.setObjectName(f'answerlabel{i}')
            qa_input_answer = QtWidgets.QLineEdit()
            qa_input_answer.setObjectName(f'answer{i}')
            qa_input_answer.setReadOnly(True)
            qa_label_answer.setMaximumWidth(100)

            qa_detail_layout.addWidget(qa_label_answer, 1+i, 0, 1, 1)
            qa_detail_layout.addWidget(qa_input_answer, 1+i, 1, 1, 1)

        self.qa_layout.addWidget(qa_detail_groupbox)

        self.script_area_groupbox = QtWidgets.QGroupBox()
        self.script_area_groupbox.setFixedHeight(450)
        self.script_area_layout = QtWidgets.QGridLayout(self.script_area_groupbox)

        self.script_label = QtWidgets.QLabel("대본")
        self.script_input = QtWidgets.QTextEdit()
        self.script_input.setMaximumHeight(150)
        self.script_input.setReadOnly(True)
        self.summary_label = QtWidgets.QLabel("요약")
        self.summary_input = QtWidgets.QTextEdit()
        self.summary_input.setMaximumHeight(300)
        self.summary_input.setReadOnly(True)
        self.summary_input.setObjectName('summary')

        self.script_area_layout.addWidget(self.script_label, 0, 0)
        self.script_area_layout.addWidget(self.script_input, 1, 0)
        self.script_area_layout.addWidget(self.summary_label, 2, 0)
        self.script_area_layout.addWidget(self.summary_input, 3, 0)

        self.control_groupbox = QtWidgets.QGroupBox()
        self.control_groupbox.setFixedHeight(50)
        self.control_area_layout = QtWidgets.QGridLayout(self.control_groupbox)
        self.prev_btn = QPushButton()
        self.prev_btn.setEnabled(False)
        self.prev_btn.setIcon(self.style().standardIcon(QStyle.SP_ArrowLeft))
        self.prev_btn.clicked.connect(self.prev_action)
        self.next_btn = QPushButton()
        self.next_btn.setEnabled(False)
        self.next_btn.setIcon(self.style().standardIcon(QStyle.SP_ArrowRight))
        self.next_btn.clicked.connect(self.next_action)

        self.control_area_layout.addWidget(self.prev_btn, 0, 0)
        self.control_area_layout.addWidget(self.next_btn, 0, 1)

        self.video_group_box.setFixedWidth(1200)

        self.main_layout.addWidget(self.video_group_box, 0, 0, 3, 1)
        self.main_layout.addWidget(self.script_area_groupbox, 0, 1, 1, 1)
        self.main_layout.addWidget(self.qa_group_box, 1, 1, 1, 1)
        self.main_layout.addWidget(self.control_groupbox, 2, 1, 1, 1)
        self.resize(1900, 786)
        self.move(100, 0)

    def open_folder(self):
        self.open_folder = str(QFileDialog.getExistingDirectory(self, "Select Directory", "./vqa_tool"))
        if not os.path.exists(os.path.join(self.open_folder, '라벨링데이터')):
            QtWidgets.QMessageBox.warning(self, "알림", "폴더 선택이 올바르지 않습니다.")
        for (root, dirs, files) in os.walk(os.path.join(self.open_folder, '라벨링데이터')):
            for file in files:
                file_name, file_ext = os.path.splitext(file)
                if '.json' == file_ext:
                    self.json_list.append(os.path.join(root, file))
        for json_file in self.json_list:
            with open(json_file, 'r', encoding='utf8') as fp:
                load_json_data = json.load(fp)
            for data in load_json_data:
                data['vid'] = os.path.join(os.path.split(json_file)[0].replace('라벨링데이터', '원천데이터'), data['vid'])
                self.json_data.append(data)

        self.set_qa_data(0)

    def prev_action(self):
        go_index = self.current_index - 1
        if go_index < 0:
            QtWidgets.QMessageBox.warning(self, "알림", "이전 데이터가 없습니다.")
        else:
            self.set_qa_data(go_index)

    def next_action(self):
        go_index = self.current_index + 1
        if go_index > len(self.json_data):
            QtWidgets.QMessageBox.warning(self, "알림", "다음 데이터가 없습니다.")
        else:
            self.set_qa_data(go_index)

    def set_qa_data(self, index):
        show_data = self.json_data[index]
        self.current_index = index
        self.media_player.setMedia(QMediaContent(QtCore.QUrl.fromLocalFile(show_data['vid'])))
        self.script_input.setText(show_data['script'])
        self.summary_input.setText(show_data['sum'])
        self.findChild(QtWidgets.QLineEdit, "question").setText(show_data['que'])
        for idx, answer in enumerate(show_data['answers']):
            self.findChild(QtWidgets.QLineEdit, f'answer{idx}').setText(answer)
            if idx == show_data['correct_idx']:
                self.findChild(QtWidgets.QLabel, f'answerlabel{idx}').setText("정답 : ")
                self.findChild(QtWidgets.QLineEdit, f'answer{idx}').setStyleSheet("background-color: yellow")
            else:
                self.findChild(QtWidgets.QLabel, f'answerlabel{idx}').setText("오답 : ")
                self.findChild(QtWidgets.QLineEdit, f'answer{idx}').setStyleSheet("background-color: white")
        self.playButton.setEnabled(True)

        if self.current_index == 0:
            self.prev_btn.setEnabled(False)
        else:
            self.prev_btn.setEnabled(True)

        if self.current_index == len(self.json_data):
            self.next_btn.setEnabled(False)
        else:
            self.next_btn.setEnabled(True)
        self.play()

    def play(self):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()

    def mediaStateChanged(self, state):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPlay))

    def positionChanged(self, position):
        self.positionSlider.setValue(position)

    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)

    def setPosition(self, position):
        self.media_player.setPosition(position)

    def handleError(self):
        self.playButton.setEnabled(False)
        self.errorLabel.setText("Error: " + self.media_player.errorString())

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = main()
    main.show()

    app.installEventFilter(main)

    sys.exit(app.exec_())
