import wx
import subprocess
import socket
import requests

class MediaSyncGUI(wx.Frame):
    def __init__(self, parent, title):
        super(MediaSyncGUI, self).__init__(parent, title=title, size=(500, 400))
        self.vlc_port = "9999"
        self.mpc_hc_port = "13579"
        self.vlc_process = None
        self.mpc_hc_process = None
        self.is_playing = False

        self.init_ui()
        self.Centre()
        self.Show()

    def init_ui(self):
        panel = wx.Panel(self)

        # VLC Port Entry
        vlc_label = wx.StaticText(panel, label="VLC Port:", pos=(10, 10))
        self.vlc_port_input = wx.TextCtrl(panel, value=self.vlc_port, pos=(80, 10))
        launch_vlc_button = wx.Button(panel, label="Launch VLC", pos=(200, 10))
        launch_vlc_button.Bind(wx.EVT_BUTTON, self.launch_vlc)

        # MPC-HC Port Entry
        mpc_label = wx.StaticText(panel, label="MPC-HC Port:", pos=(10, 50))
        self.mpc_hc_port_input = wx.TextCtrl(panel, value=self.mpc_hc_port, pos=(80, 50))
        launch_mpc_button = wx.Button(panel, label="Launch MPC-HC", pos=(200, 50))
        launch_mpc_button.Bind(wx.EVT_BUTTON, self.launch_mpc_hc)

        # Media launch buttons
        launch_vlc_media_button = wx.Button(panel, label="Launch VLC with Media", pos=(10, 90))
        launch_vlc_media_button.Bind(wx.EVT_BUTTON, lambda event: self.launch_vlc(with_media=True))

        launch_mpc_media_button = wx.Button(panel, label="Launch MPC-HC with Media", pos=(200, 90))
        launch_mpc_media_button.Bind(wx.EVT_BUTTON, lambda event: self.launch_mpc_hc(with_media=True))

        # Playback controls
        play_button = wx.Button(panel, label="Play", pos=(10, 130))
        play_button.Bind(wx.EVT_BUTTON, self.play)

        pause_button = wx.Button(panel, label="Pause", pos=(100, 130))
        pause_button.Bind(wx.EVT_BUTTON, self.pause)

        next_button = wx.Button(panel, label="Next Chapter", pos=(200, 130))
        next_button.Bind(wx.EVT_BUTTON, self.next_chapter)

        previous_button = wx.Button(panel, label="Previous Chapter", pos=(300, 130))
        previous_button.Bind(wx.EVT_BUTTON, self.previous_chapter)

        # Speed control dropdown
        speed_label = wx.StaticText(panel, label="Playback Speed:", pos=(10, 170))
        self.speed_dropdown = wx.ComboBox(panel, choices=["1x", "2x", "4x", "8x", "16x", "32x"], pos=(110, 170))
        self.speed_dropdown.SetValue("1x")
        set_speed_button = wx.Button(panel, label="Set Speed", pos=(200, 170))
        set_speed_button.Bind(wx.EVT_BUTTON, self.set_speed)

    def launch_vlc(self, event, with_media=False):
        if self.vlc_process:
            self.vlc_process.terminate()
        media_file = ""
        if with_media:
            with wx.FileDialog(self, "Select Media File for VLC", wildcard="All files (*.*)|*.*",
                               style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
                if fileDialog.ShowModal() == wx.ID_CANCEL:
                    return
                media_file = fileDialog.GetPath()
        self.vlc_process = subprocess.Popen(
            ["vlc", f"--extraintf=rc", f"--rc-host=localhost:{self.vlc_port_input.GetValue()}", media_file],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

    def launch_mpc_hc(self, event, with_media=False):
        if self.mpc_hc_process:
            self.mpc_hc_process.terminate()
        media_file = ""
        if with_media:
            with wx.FileDialog(self, "Select Media File for MPC-HC", wildcard="All files (*.*)|*.*",
                               style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
                if fileDialog.ShowModal() == wx.ID_CANCEL:
                    return
                media_file = fileDialog.GetPath()
        self.mpc_hc_process = subprocess.Popen(
            ["mpc-hc64", "/play", media_file],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

    def send_vlc_command(self, command):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(("localhost", int(self.vlc_port_input.GetValue())))
            sock.send(f"{command}\n".encode())
            sock.close()
        except Exception as e:
            print(f"VLC command failed: {e}")

    def send_mpc_hc_command(self, command):
        try:
            requests.get(f"http://localhost:{self.mpc_hc_port_input.GetValue()}/command.html?wm_command={command}")
        except Exception as e:
            print(f"MPC-HC command failed: {e}")

    def play(self, event):
        self.send_vlc_command("play")
        self.send_mpc_hc_command("887")  # Play command for MPC-HC

    def pause(self, event):
        self.send_vlc_command("pause")
        self.send_mpc_hc_command("888")  # Pause command for MPC-HC

    def play_pause_toggle(self, event):
        if self.is_playing:
            self.pause()
        else:
            self.play()
        self.is_playing = not self.is_playing

    def next_chapter(self, event):
        self.send_vlc_command("next")
        self.send_mpc_hc_command("922")  # Next chapter command for MPC-HC

    def previous_chapter(self, event):
        self.send_vlc_command("prev")
        self.send_mpc_hc_command("921")  # Previous chapter command for MPC-HC

    def set_speed(self, event):
        speed = self.speed_dropdown.GetValue().replace("x", "")
        self.send_vlc_command(f"rate {speed}")
        multiplier = int(speed)
        for _ in range(multiplier):
            self.send_mpc_hc_command("891")  # Increment speed by 10% for each step

if __name__ == '__main__':
    app = wx.App(False)
    frame = MediaSyncGUI(None, "Media Sync Controller")
    app.MainLoop()
