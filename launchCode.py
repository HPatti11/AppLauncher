import tkinter as tk
from PIL import Image, ImageTk
import os
import cv2

# ----------------- CONFIG -----------------
ICON_SIZE = (200, 200)      # width, height in pixels
BG_IMAGE = "imgs/Harumasa.png"  # fullscreen background
BUTTON_ACTIVE_BG = "#aaaaaa"

# ----------------- APP LAUNCH FUNCTIONS -----------------
def open_chrome():
    os.system("open -a 'Google Chrome' &")
    os._exit(0)
def open_facetime():
    os.system("open -a 'FaceTime' &")
    os._exit(0)
def open_roblox():
    os.system("open -a 'Roblox' &")
    os._exit(0)
def open_vscode():
    if os.system("which code > /dev/null 2>&1") == 0:
        os.system("code &")
    else:
        os.system("open -a 'Visual Studio Code' &")
    os._exit(0)
launch_map = {
    "chrome": open_chrome,
    "facetime": open_facetime,
    "roblox": open_roblox,
    "vscode": open_vscode,
}

# ----------------- TKINTER WINDOW -----------------
root = tk.Tk()
root.attributes("-fullscreen", True)
root.title("My Full Screen Launcher")

def on_key(event):
    if event.keysym == "Escape":
        root.destroy()
    elif event.keysym.lower() == "q":
        os._exit(0)

root.bind("<Key>", on_key)

# ----------------- BACKGROUND RENDERING HELPERS -----------------

canvas = tk.Canvas(root, width=root.winfo_screenwidth(), height=root.winfo_screenheight())
canvas.pack(fill="both", expand=True)

gif_frames = None
gif_durations = None
video_cap = None

def play_static_background(path):
    try:
        img = Image.open(path).convert("RGBA")
        img = img.resize((root.winfo_screenwidth(), root.winfo_screenheight()), Image.Resampling.LANCZOS)
        bg = ImageTk.PhotoImage(img)
        canvas.img_ref = bg
        canvas.create_image(0, 0, anchor="nw", image=bg)
    except Exception as e:
        print("Static background error:", e)


def play_gif_background(gif_path):
    canvas.delete("all")

    try:
        gif = Image.open(gif_path)
    except Exception as e:
        print(f"Failed to load GIF background: {e}")
        return

    frames = []
    durations = []

    # Load all frames into memory FIRST (much faster playback)
    try:
        while True:
            frame = gif.copy().convert("RGBA")
            frame = frame.resize((root.winfo_screenwidth(), root.winfo_screenheight()))
            frames.append(ImageTk.PhotoImage(frame))

            # ignore GIF delay and force fast refresh
            durations.append(16)  # ~60fps
            gif.seek(gif.tell() + 1)
    except EOFError:
        pass

    # Create image once (we just update its contents)
    image_on_canvas = canvas.create_image(0, 0, anchor="nw", image=frames[0])
    canvas.img_ref = frames[0]  # prevent GC

    def animate(index=0):
        frame = frames[index]
        canvas.itemconfig(image_on_canvas, image=frame)
        canvas.img_ref = frame
        next_index = (index + 1) % len(frames)
        root.after(durations[index], animate, next_index)

    animate()


def play_video_background(path):
    global video_cap
    canvas.delete("all")
    video_cap = cv2.VideoCapture(path)

    def update():
        global video_cap
        if video_cap is None:
            return

        ret, frame = video_cap.read()
        if not ret:
            video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            return root.after(30, update)

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        frame = cv2.resize(frame, (root.winfo_screenwidth(), root.winfo_screenheight()))
        img = ImageTk.PhotoImage(Image.fromarray(frame))

        canvas.img_ref = img
        canvas.create_image(0, 0, anchor="nw", image=img)

        root.after(30, update)

    update()

# Decide what type of background to play
lower = BG_IMAGE.lower()

if lower.endswith(".mp4") or lower.endswith(".mov"):
    play_video_background(BG_IMAGE)
elif lower.endswith(".gif"):
    play_gif_background(BG_IMAGE)
else:
    play_static_background(BG_IMAGE)

# ----------------- LOAD ICONS -----------------
def load_icon(filename):
    try:
        img = Image.open(filename).convert("RGBA")
        img = img.resize(ICON_SIZE, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img)
    except:
        return ImageTk.PhotoImage(Image.new("RGBA", ICON_SIZE, (128,128,128,255)))

chrome_logo   = load_icon("imgs/chrome.png")
facetime_logo = load_icon("imgs/facetime.png")
roblox_logo   = load_icon("imgs/roblox.png")
vscode_logo   = load_icon("imgs/vscode.png")

# ----------------- BUTTON GRID -----------------
buttons = {
    "chrome": chrome_logo,
    "facetime": facetime_logo,
    "roblox": roblox_logo,
    "vscode": vscode_logo,
}

row_col_map = {
    "chrome": (0, 0),
    "facetime": (0, 1),
    "roblox": (1, 0),
    "vscode": (1, 1),
}

btn_widgets = {}
for name, img in buttons.items():
    r, c = row_col_map[name]
    x = (c + 0.5) * root.winfo_screenwidth() / 2
    y = (r + 0.5) * root.winfo_screenheight() / 2
    btn = tk.Button(root, image=img, activebackground=BUTTON_ACTIVE_BG,
                    command=launch_map[name], relief="flat", borderwidth=0)
    btn_widgets[name] = btn
    canvas.create_window(x, y, window=btn, anchor="center")

root.mainloop()
