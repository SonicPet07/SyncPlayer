import tkinter as tk
from tkinter import ttk, filedialog
from MediaControls import MediaControls

class MediaSyncGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Media Sync Controller")

        # Player launch options
        self.vlc_port = tk.StringVar(value="9999")
        self.mpc_hc_port = tk.StringVar(value="13579")
        self.media_controls = MediaControls()
        self.vlc_process = None
        self.mpc_hc_process = None
        self.is_playing = False


        self.create_widgets()
        self.bind_shortcuts()


    def create_widgets(self):
        # VLC Port Entry
        tk.Label(self, text="VLC Port:").grid(row=0, column=0, padx=5, pady=5)
        tk.Entry(self, textvariable=self.vlc_port).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(self, text="Launch VLC", command=self.launch_vlc_helper).grid(row=0, column=2, padx=5, pady=5)

        # MPC-HC Port Entry
        tk.Label(self, text="MPC-HC Port:").grid(row=1, column=0, padx=5, pady=5)
        tk.Entry(self, textvariable=self.mpc_hc_port).grid(row=1, column=1, padx=5, pady=5)
        tk.Button(self, text="Launch MPC-HC", command=self.launch_mpc_hc_helper).grid(row=1, column=2, padx=5, pady=5)

        # Media launch buttons
        tk.Button(self, text="Launch VLC with Media", command=lambda: self.launch_vlc_helper(with_media=True)).grid(row=2, column=0, padx=5, pady=5)
        tk.Button(self, text="Launch MPC-HC with Media", command=lambda: self.launch_mpc_hc_helper(with_media=True)).grid(row=2, column=1, padx=5, pady=5)

        # Playback controls
        tk.Button(self, text="Play", command=self.media_controls.play).grid(row=3, column=0, padx=5, pady=5)
        tk.Button(self, text="Pause", command=self.media_controls.pause).grid(row=3, column=1, padx=5, pady=5)
        tk.Button(self, text="Next Chapter", command=self.media_controls.next_chapter).grid(row=3, column=2, padx=5, pady=5)
        tk.Button(self, text="Previous Chapter", command=self.media_controls.previous_chapter).grid(row=3, column=3, padx=5, pady=5)

        # Speed control dropdown
        tk.Label(self, text="Playback Speed:").grid(row=4, column=0, padx=5, pady=5)
        self.speed_dropdown = tk.StringVar(value="1x")
        self.speed_dropdown = ttk.Combobox(self, textvariable=self.speed_dropdown, values=["1x", "2x", "4x", "8x", "16x", "32x"])
        self.speed_dropdown.grid(row=4, column=1, padx=5, pady=5)
        tk.Button(self, text="Set Speed", command=self.set_speed_helper).grid(row=4, column=2, padx=5, pady=5)

    def bind_shortcuts(self):
        # Bind keyboard shortcuts
        self.bind('<space>', lambda event: self.play_pause_toggle())
        self.bind('<Right>', lambda event: self.next_chapter())
        self.bind('<Left>', lambda event: self.previous_chapter())

    def launch_vlc_helper(self, with_media=False):
        media_file = ""
        if with_media:
            media_file = filedialog.askopenfilename(title="Select Media File for VLC")
        self.media_controls.launch_vlc(media_file=media_file, port=self.vlc_port.get())


    def launch_mpc_hc_helper(self, with_media=False):
        media_file = ""
        if with_media:
            media_file = filedialog.askopenfilename(title="Select Media File for MPC-HC")
        self.media_controls.launch_mpc_hc(
            media_file=media_file,
            port=self.mpc_hc_port.get()
            )

    def set_speed_helper(self):
        speed = self.speed_dropdown.get().replace("x", "")
        self.media_controls.set_speed(speed)


# Run the GUI

app = MediaSyncGUI()
app.mainloop()
