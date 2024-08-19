from fastapi import FastAPI, Request, WebSocket
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import subprocess
import socket
import requests
import signal
import sys


app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Mount the static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")


# Player ports
vlc_port = 9999
mpc_hc_port = 13579

# Track player state and processes
is_playing = False
vlc_process = None
mpc_hc_process = None

# Launch VLC
def launch_vlc(with_media: bool = False, media_file: str = ""):
    global vlc_process
    if vlc_process:
        vlc_process.terminate()
    command = ["vlc", f"--extraintf=rc", f"--rc-host=localhost:{vlc_port}"]
    if with_media:
        command.append(media_file)
    vlc_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# Launch MPC-HC
def launch_mpc_hc(with_media: bool = False, media_file: str = ""):
    global mpc_hc_process
    if mpc_hc_process:
        mpc_hc_process.terminate()
    command = ["mpc-hc64", "/play"]
    if with_media:
        command.append(media_file)
    mpc_hc_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# Send command to VLC
def send_vlc_command(command: str):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(("localhost", vlc_port))
        sock.send(f"{command}\n".encode())
        sock.close()
    except Exception as e:
        print(f"VLC command failed: {e}")

# Send command to MPC-HC
def send_mpc_hc_command(command: str):
    try:
        requests.get(f"http://localhost:{mpc_hc_port}/command.html?wm_command={command}")
    except Exception as e:
        print(f"MPC-HC command failed: {e}")

# Play/Pause Toggle
@app.post("/toggle_play_pause")
async def toggle_play_pause():
    global is_playing
    if is_playing:
        send_vlc_command("pause")
        send_mpc_hc_command("888")  # Pause command
    else:
        send_vlc_command("play")
        send_mpc_hc_command("887")  # Play command
    is_playing = not is_playing
    return {"is_playing": is_playing}

# Next Chapter
@app.post("/next_chapter")
async def next_chapter():
    send_vlc_command("next")
    send_mpc_hc_command("922")  # Next chapter command
    return {"status": "next chapter"}

# Previous Chapter
@app.post("/previous_chapter")
async def previous_chapter():
    send_vlc_command("prev")
    send_mpc_hc_command("921")  # Previous chapter command
    return {"status": "previous chapter"}

# Set Speed
@app.post("/set_speed")
async def set_speed(request: Request):
    data = await request.form()
    speed = data["speed"]
    send_vlc_command(f"rate {speed}")
    multiplier = int(speed)
    for _ in range(multiplier):
        send_mpc_hc_command("891")  # Increment speed by 10%
    return {"status": f"speed set to {speed}x"}

# WebSocket for real-time control
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        if data == "toggle_play_pause":
            await toggle_play_pause()
        elif data == "next_chapter":
            await next_chapter()
        elif data == "previous_chapter":
            await previous_chapter()
        # Send feedback back to the client
        await websocket.send_text(f"Action {data} completed")

# Home page
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Graceful shutdown
def cleanup(signum, frame):
    print("Shutting down...")
    if vlc_process:
        vlc_process.terminate()
    if mpc_hc_process:
        mpc_hc_process.terminate()
    sys.exit(0)

# Attach signal handler for graceful shutdown
signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
