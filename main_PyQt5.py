from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QPushButton, QComboBox, QVBoxLayout, QHBoxLayout)
import subprocess
import socket
import requests

class MediaSyncGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Media Sync Controller")
        self.vlc_port = "9999"
        self.mpc_hc_port = "13579"
        self.vlc_process = None
        self.mpc_hc_process = None
        self.is_playing = False

        self.init_ui()

    def init_ui(self):
        # VLC Port Entry
        vlc_label = QLabel("VLC Port:")
        self.vlc_port_input = QLineEdit(self.vlc_port)
        launch_vlc_button = QPushButton("Launch VLC")
        launch_vlc_button.clicked.connect(self.launch_vlc)

        # MPC-HC Port Entry
        mpc_label = QLabel("MPC-HC Port:")
        self.mpc_hc_port_input = QLineEdit(self.mpc_hc_port)
        launch_mpc_button = QPushButton("Launch MPC-HC")
        launch_mpc_button.clicked.connect(self.launch_mpc_hc)

        # Media launch buttons
        launch_vlc_media_button = QPushButton("Launch VLC with Media")
        launch_vlc_media_button.clicked.connect(lambda: self.launch_vlc(with_media=True))

        launch_mpc_media_button = QPushButton("Launch MPC-HC with Media")
        launch_mpc_media_button.clicked.connect(lambda: self.launch_mpc_hc(with_media=True))

        # Playback controls
        play_button = QPushButton("Play")
        play_button.clicked.connect(self.play)

        pause_button = QPushButton("Pause")
        pause_button.clicked.connect(self.pause)

        next_button = QPushButton("Next Chapter")
        next_button.clicked.connect(self.next_chapter)

        previous_button = QPushButton("Previous Chapter")
        previous_button.clicked.connect(self.previous_chapter)

        # Speed control dropdown
        speed_label = QLabel("Playback Speed:")
        self.speed_dropdown = QComboBox()
        self.speed_dropdown.addItems(["1x", "2x", "4x", "8x", "16x", "32x"])
        set_speed_button = QPushButton("Set Speed")
        set_speed_button.clicked.connect(self.set_speed)

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

    def launch_vlc(self, with_media=False):
        if self.vlc_process:
            self.vlc_process.terminate()
        media_file = ""
        if with_media:
            media_file = filedialog.getOpenFileName(self, "Select Media File for VLC")[0]
        self.vlc_process = subprocess.Popen(
            ["vlc", f"--extraintf=rc", f"--rc-host=localhost:{self.vlc_port_input.text()}", media_file],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

    def launch_mpc_hc(self, with_media=False):
        if self.mpc_hc_process:
            self.mpc_hc_process.terminate()
        media_file = ""
        if with_media:
            media_file = filedialog.getOpenFileName(self, "Select Media File for MPC-HC")[0]
        self.mpc_hc_process = subprocess.Popen(
            ["mpc-hc64", "/play", media_file],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

    def send_vlc_command(self, command):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(("localhost", int(self.vlc_port_input.text())))
            sock.send(f"{command}\n".encode())
            sock.close()
        except Exception as e:
            print(f"VLC command failed: {e}")

    def send_mpc_hc_command(self, command):
        try:
            requests.get(f"http://localhost:{self.mpc_hc_port_input.text()}/command.html?wm_command={command}")
        except Exception as e:
            print(f"MPC-HC command failed: {e}")

    def play(self):
        self.send_vlc_command("play")
        self.send_mpc_hc_command("887")  # Play command for MPC-HC

    def pause(self):
        self.send_vlc_command("pause")
        self.send_mpc_hc_command("888")  # Pause command for MPC-HC

    def play_pause_toggle(self):
        if self.is_playing:
            self.pause()
        else:
            self.play()
        self.is_playing = not self.is_playing

    def next_chapter(self):
        self.send_vlc_command("next")
        self.send_mpc_hc_command("922")  # Next chapter command for MPC-HC

    def previous_chapter(self):
        self.send_vlc_command("prev")
        self.send_mpc_hc_command("921")  # Previous chapter command for MPC-HC

    def set_speed(self):
        speed = self.speed_dropdown.currentText().replace("x", "")
        self.send_vlc_command(f"rate {speed}")
        multiplier = int(speed)
        for _ in range(multiplier):
            self.send_mpc_hc_command("891")  # Increment speed by 10% for each step

if __name__ == '__main__':
    app = QApplication([])
    gui = MediaSyncGUI()
    gui.show()
    app.exec_()


