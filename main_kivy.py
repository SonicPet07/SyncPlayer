from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.core.window import Window
import subprocess
import socket
import requests
from kivy.uix.filechooser import FileChooserListView

class MediaSyncGUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.vlc_process = None
        self.mpc_hc_process = None
        self.is_playing = False

        # VLC Port Entry
        vlc_label = Label(text="VLC Port:")
        self.vlc_port_input = TextInput(text="9999")
        vlc_button = Button(text="Launch VLC")
        vlc_button.bind(on_press=self.launch_vlc)

        # MPC-HC Port Entry
        mpc_label = Label(text="MPC-HC Port:")
        self.mpc_hc_port_input = TextInput(text="13579")
        mpc_button = Button(text="Launch MPC-HC")
        mpc_button.bind(on_press=self.launch_mpc_hc)

        # Media launch buttons
        launch_vlc_media_button = Button(text="Launch VLC with Media")
        launch_vlc_media_button.bind(on_press=lambda x: self.launch_vlc(with_media=True))

        launch_mpc_media_button = Button(text="Launch MPC-HC with Media")
        launch_mpc_media_button.bind(on_press=lambda x: self.launch_mpc_hc(with_media=True))

        # Playback controls
        play_button = Button(text="Play")
        play_button.bind(on_press=self.play)

        pause_button = Button(text="Pause")
        pause_button.bind(on_press=self.pause)

        next_button = Button(text="Next Chapter")
        next_button.bind(on_press=self.next_chapter)

        previous_button = Button(text="Previous Chapter")
        previous_button.bind(on_press=self.previous_chapter)

        # Speed control dropdown
        speed_label = Label(text="Playback Speed:")
        self.speed_spinner = Spinner(
            text="1x",
            values=["1x", "2x", "4x", "8x", "16x", "32x"]
        )
        set_speed_button = Button(text="Set Speed")
        set_speed_button.bind(on_press=self.set_speed)

        # Add widgets to layout
        self.add_widget(vlc_label)
        self.add_widget(self.vlc_port_input)
        self.add_widget(vlc_button)
        self.add_widget(mpc_label)
        self.add_widget(self.mpc_hc_port_input)
        self.add_widget(mpc_button)
        self.add_widget(launch_vlc_media_button)
        self.add_widget(launch_mpc_media_button)
        self.add_widget(play_button)
        self.add_widget(pause_button)
        self.add_widget(next_button)
        self.add_widget(previous_button)
        self.add_widget(speed_label)
        self.add_widget(self.speed_spinner)
        self.add_widget(set_speed_button)

    def launch_vlc(self, with_media=False):
        if self.vlc_process:
            self.vlc_process.terminate()
        media_file = ""
        if with_media:
            filechooser = FileChooserListView()
            self.add_widget(filechooser)
            media_file = filechooser.selection[0]
        self.vlc_process = subprocess.Popen(
            ["vlc", f"--extraintf=rc", f"--rc-host=localhost:{self.vlc_port_input.text}", media_file],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

    def launch_mpc_hc(self, with_media=False):
        if self.mpc_hc_process:
            self.mpc_hc_process.terminate()
        media_file = ""
        if with_media:
            filechooser = FileChooserListView()
            self.add_widget(filechooser)
            media_file = filechooser.selection[0]
        self.mpc_hc_process = subprocess.Popen(
            ["mpc-hc64", "/play", media_file],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

    def send_vlc_command(self, command):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(("localhost", int(self.vlc_port_input.text)))
            sock.send(f"{command}\n".encode())
            sock.close()
        except Exception as e:
            print(f"VLC command failed: {e}")

    def send_mpc_hc_command(self, command):
        try:
            requests.get(f"http://localhost:{self.mpc_hc_port_input.text}/command.html?wm_command={command}")
        except Exception as e:
            print(f"MPC-HC command failed: {e}")

    def play(self, instance):
        self.send_vlc_command("play")
        self.send_mpc_hc_command("887")  # Play command for MPC-HC

    def pause(self, instance):
        self.send_vlc_command("pause")
        self.send_mpc_hc_command("888")  # Pause command for MPC-HC

    def play_pause_toggle(self, instance):
        if self.is_playing:
            self.pause()
        else:
            self.play()
        self.is_playing = not self.is_playing

    def next_chapter(self, instance):
        self.send_vlc_command("next")
        self.send_mpc_hc_command("922")  # Next chapter command for MPC-HC

    def previous_chapter(self, instance):
        self.send_vlc_command("prev")
        self.send_mpc_hc_command("921")  # Previous chapter command for MPC-HC

    def set_speed(self, instance):
        speed = self.speed_spinner.text.replace("x", "")
        self.send_vlc_command(f"rate {speed}")
        multiplier = int(speed)
        for _ in range(multiplier):
            self.send_mpc_hc_command("891")  # Increment speed by 10% for each step

class MediaSyncApp(App):
    def build(self):
        return MediaSyncGUI()

if __name__ == '__main__':
    MediaSyncApp().run()
