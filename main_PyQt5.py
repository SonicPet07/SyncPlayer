from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QPushButton, QComboBox, QVBoxLayout, QHBoxLayout, QFileDialog)
from MediaControls import MediaControls
import subprocess

class MediaSyncGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Media Sync Controller")
        self.vlc_port = "9999"
        self.mpc_hc_port = "13579"
        self.media_controls = MediaControls()
        self.vlc_process = None
        self.mpc_hc_process = None
        self.is_playing = False

        self.init_ui()

    def init_ui(self):
        # VLC Port Entry
        vlc_label = QLabel("VLC Port:")
        self.vlc_port_input = QLineEdit(self.vlc_port)
        launch_vlc_button = QPushButton("Launch VLC")
        launch_vlc_button.clicked.connect(self.launch_vlc_helper)

        # MPC-HC Port Entry
        mpc_label = QLabel("MPC-HC Port:")
        self.mpc_hc_port_input = QLineEdit(self.mpc_hc_port)
        launch_mpc_button = QPushButton("Launch MPC-HC")
        launch_mpc_button.clicked.connect(self.launch_mpc_hc_helper)

        # Media launch buttons
        launch_vlc_media_button = QPushButton("Launch VLC with Media")
        launch_vlc_media_button.clicked.connect(lambda: self.launch_vlc_helper(with_media=True))

        launch_mpc_media_button = QPushButton("Launch MPC-HC with Media")
        launch_mpc_media_button.clicked.connect(lambda: self.launch_mpc_hc_helper(with_media=True))

        # Playback controls
        play_button = QPushButton("Play")
        play_button.clicked.connect(self.media_controls.play)

        pause_button = QPushButton("Pause")
        pause_button.clicked.connect(self.media_controls.pause)

        next_button = QPushButton("Next Chapter")
        next_button.clicked.connect(self.media_controls.next_chapter)

        previous_button = QPushButton("Previous Chapter")
        previous_button.clicked.connect(self.media_controls.previous_chapter)

        # Speed control dropdown
        speed_label = QLabel("Playback Speed:")
        self.speed_dropdown = QComboBox()
        self.speed_dropdown.addItems(["1x", "2x", "4x", "8x", "16x", "32x"])
        set_speed_button = QPushButton("Set Speed")
        set_speed_button.clicked.connect(self.set_speed_helper)

        # Layouts
        layout = QVBoxLayout()

        port_layout = QHBoxLayout()
        port_layout.addWidget(vlc_label)
        port_layout.addWidget(self.vlc_port_input)
        port_layout.addWidget(launch_vlc_button)
        layout.addLayout(port_layout)

        port_layout2 = QHBoxLayout()
        port_layout2.addWidget(mpc_label)
        port_layout2.addWidget(self.mpc_hc_port_input)
        port_layout2.addWidget(launch_mpc_button)
        layout.addLayout(port_layout2)

        media_layout = QHBoxLayout()
        media_layout.addWidget(launch_vlc_media_button)
        media_layout.addWidget(launch_mpc_media_button)
        layout.addLayout(media_layout)

        controls_layout = QHBoxLayout()
        controls_layout.addWidget(play_button)
        controls_layout.addWidget(pause_button)
        controls_layout.addWidget(next_button)
        controls_layout.addWidget(previous_button)
        layout.addLayout(controls_layout)

        speed_layout = QHBoxLayout()
        speed_layout.addWidget(speed_label)
        speed_layout.addWidget(self.speed_dropdown)
        speed_layout.addWidget(set_speed_button)
        layout.addLayout(speed_layout)

        self.setLayout(layout)

    def launch_vlc_helper(self, with_media=False):
        media_file = ""
        if with_media:
            media_file, _ = QFileDialog.getOpenFileName(self, "Select Media File for VLC")
        self.media_controls.launch_vlc(media_file=media_file, port=self.vlc_port_input.text())

    def launch_mpc_hc_helper(self, with_media=False):
        media_file = ""
        if with_media:
            media_file = QFileDialog.getOpenFileName(self, "Select Media File for MPC-HC")[0]
        self.media_controls.launch_mpc_hc(
            media_file=media_file,
            port=self.mpc_hc_port_input.text()
            )

    def set_speed_helper(self):
        speed = self.speed_dropdown.currentText().replace("x", "")
        self.media_controls.set_speed(speed)

if __name__ == '__main__':
    app = QApplication([])
    gui = MediaSyncGUI()
    gui.show()
    app.exec_()


