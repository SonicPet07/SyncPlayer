import tkinter as tk
from tkinter import ttk, filedialog
import subprocess
import socket
import requests

class MediaSyncGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Media Sync Controller")

        # Player launch options
        self.vlc_port = tk.StringVar(value="9999")
        self.mpc_hc_port = tk.StringVar(value="13579")
        self.vlc_process = None
        self.mpc_hc_process = None
        self.is_playing = False


        self.create_widgets()
        self.bind_shortcuts()


    def create_widgets(self):
        # VLC Port Entry
        tk.Label(self.root, text="VLC Port:").grid(row=0, column=0, padx=5, pady=5)
        tk.Entry(self.root, textvariable=self.vlc_port).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(self.root, text="Launch VLC", command=self.launch_vlc).grid(row=0, column=2, padx=5, pady=5)

        # MPC-HC Port Entry
        tk.Label(self.root, text="MPC-HC Port:").grid(row=1, column=0, padx=5, pady=5)
        tk.Entry(self.root, textvariable=self.mpc_hc_port).grid(row=1, column=1, padx=5, pady=5)
        tk.Button(self.root, text="Launch MPC-HC", command=self.launch_mpc_hc).grid(row=1, column=2, padx=5, pady=5)

        # Media launch buttons
        tk.Button(self.root, text="Launch VLC with Media", command=lambda: self.launch_vlc(with_media=True)).grid(row=2, column=0, padx=5, pady=5)
        tk.Button(self.root, text="Launch MPC-HC with Media", command=lambda: self.launch_mpc_hc(with_media=True)).grid(row=2, column=1, padx=5, pady=5)

        # Playback controls
        tk.Button(self.root, text="Play", command=self.play).grid(row=3, column=0, padx=5, pady=5)
        tk.Button(self.root, text="Pause", command=self.pause).grid(row=3, column=1, padx=5, pady=5)
        tk.Button(self.root, text="Next Chapter", command=self.next_chapter).grid(row=3, column=2, padx=5, pady=5)
        tk.Button(self.root, text="Previous Chapter", command=self.previous_chapter).grid(row=3, column=3, padx=5, pady=5)

        # Speed control dropdown
        tk.Label(self.root, text="Playback Speed:").grid(row=4, column=0, padx=5, pady=5)
        self.speed_var = tk.StringVar(value="1x")
        self.speed_dropdown = ttk.Combobox(self.root, textvariable=self.speed_var, values=["1x", "2x", "4x", "8x", "16x", "32x"])
        self.speed_dropdown.grid(row=4, column=1, padx=5, pady=5)
        tk.Button(self.root, text="Set Speed", command=self.set_speed).grid(row=4, column=2, padx=5, pady=5)

    def bind_shortcuts(self):
        # Bind keyboard shortcuts
        self.root.bind('<space>', lambda event: self.play_pause_toggle())
        self.root.bind('<Right>', lambda event: self.next_chapter())
        self.root.bind('<Left>', lambda event: self.previous_chapter())

    def launch_vlc(self, with_media=False):
        if self.vlc_process:
            self.vlc_process.terminate()
        media_file = ""
        if with_media:
            media_file = filedialog.askopenfilename(title="Select Media File for VLC")
        vlc_path = r"C:\Program Files\VideoLAN\VLC\vlc.exe"
        self.vlc_process = subprocess.Popen(
            [vlc_path, "--extraintf=rc", f"--rc-host=localhost:{self.vlc_port.get()}", media_file],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

    def launch_mpc_hc(self, with_media=False):
        if self.mpc_hc_process:
            self.mpc_hc_process.terminate()
        media_file = ""
        if with_media:
            media_file = filedialog.askopenfilename(title="Select Media File for MPC-HC")
        mpc_path = r"C:\Program Files\MPC-HC\mpc-hc64.exe"
        self.mpc_hc_process = subprocess.Popen(
            [mpc_path, "/play", media_file],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

    def send_vlc_command(self, command):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(("localhost", int(self.vlc_port.get())))
            sock.send(f"{command}\n".encode())
            sock.close()
        except Exception as e:
            print(f"VLC command failed: {e}")

    def send_mpc_hc_command(self, command):
        try:
            requests.get(f"http://localhost:{self.mpc_hc_port.get()}/command.html?wm_command={command}")
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

    def set_speed(self):
        speed = self.speed_var.get().replace("x", "")
        self.send_vlc_command(f"rate {speed}")
        multiplier = int(speed)
        for _ in range(multiplier):
            self.send_mpc_hc_command("891")  # Increment speed by 10% for each step

# Run the GUI
root = tk.Tk()
app = MediaSyncGUI(root)
root.mainloop()
