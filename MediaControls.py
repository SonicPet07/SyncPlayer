import subprocess
import socket
import requests


class MediaControls:

    def __init__(self) -> None:
        self.vlc_process = None
        self.mpc_hc_process = None
        self.is_playing = False
        self.vlc_port = 0
        self.mpc_hc_port = 0

    def launch_vlc(self, media_file, port):
        if self.vlc_process:
            self.vlc_process.terminate()
        self.vlc_port = port
        vlc_path = r"C:\Program Files\VideoLAN\VLC\vlc.exe"
        self.vlc_process = subprocess.Popen(
            [vlc_path, "--extraintf=rc", f"--rc-host=localhost:{port}", media_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def launch_mpc_hc(self, media_file, port):
        if self.mpc_hc_process:
            self.mpc_hc_process.terminate()
            self.mpc_hc_port = port
        mpc_path = r"C:\Program Files\MPC-HC\mpc-hc64.exe"
        self.mpc_hc_process = subprocess.Popen(
            [mpc_path, "/play", media_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

    def send_vlc_command(self, command):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(("localhost", int(self.vlc_port)))
            sock.send(f"{command}\n".encode())
            sock.close()
        except Exception as e:
            print(f"VLC command failed: {e}")

    def send_mpc_hc_command(self, command):
        try:
            requests.get(f"http://localhost:{self.mpc_hc_port}/command.html?wm_command={command}")
        except Exception as e:
            print(f"MPC-HC command failed: {e}")

    def play(self):
        self.send_vlc_command("play")
        self.send_mpc_hc_command("887")  # Play command for MPC-HC

    def pause(self):
        self.send_vlc_command("pause")
        self.send_mpc_hc_command("888")  # Pause command for MPC-HC

    # Add this attribute in the __init__ method to track play/pause state

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

    def set_speed(self, speed):
        self.send_vlc_command(f"rate {speed}")
        multiplier = int(speed)
        for _ in range(multiplier):
            self.send_mpc_hc_command("891")  # Increment speed by 10% for each step
