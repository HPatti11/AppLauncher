import tkinter as tk
from PIL import Image, ImageTk
import os

# ----------------- CONFIG -----------------
ICON_SIZE = (200, 200)      # width, height in pixels
BG_IMAGE = "Harumasa.png" # full-screen background image
BUTTON_ACTIVE_BG = "#aaaaaa"

# ----------------- APP LAUNCH FUNCTIONS -----------------
def open_chrome():
    os.system("open -a 'Google Chrome' &")

def open_facetime():
    os.system("open -a 'FaceTime' &")

def open_roblox():
    os.system("open -a 'Roblox' &")

def open_vscode():
    if os.system("which code > /dev/null 2>&1") == 0:
        os.system("code &")
    else:
        os.system("open -a 'Visual Studio Code' &")

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

# ----------------- BACKGROUND IMAGE -----------------
def load_background_image(filename):
    try:
        img = Image.open(filename).convert("RGBA")
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        img = img.resize((screen_width, screen_height), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception as e:
        print(f"Failed to load background {filename}: {e}")
        return None

bg_img = load_background_image(BG_IMAGE)

canvas = tk.Canvas(root, width=root.winfo_screenwidth(), height=root.winfo_screenheight())
canvas.pack(fill="both", expand=True)
if bg_img:
    canvas.create_image(0, 0, anchor="nw", image=bg_img)

# ----------------- LOAD ICONS WITH TRANSPARENCY -----------------
def load_icon(filename):
    try:
        img = Image.open(filename).convert("RGBA")
        img = img.resize(ICON_SIZE, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception as e:
        print(f"Failed to load {filename}: {e}")
        placeholder = Image.new("RGBA", ICON_SIZE, (128,128,128,255))
        return ImageTk.PhotoImage(placeholder)

chrome_logo   = load_icon("chrome.png")
facetime_logo = load_icon("facetime.png")
roblox_logo   = load_icon("roblox.png")
vscode_logo   = load_icon("vscode.png")

# ----------------- BUTTON GRID -----------------
buttons = {
    "chrome": chrome_logo,
    "facetime": facetime_logo,
    "roblox": roblox_logo,
    "vscode": vscode_logo,
}

# Position buttons in a 2x2 grid
row_col_map = {
    "chrome": (0, 0),
    "facetime": (0, 1),
    "roblox": (1, 0),
    "vscode": (1, 1),
}

# Create buttons on the canvas
btn_widgets = {}
for name, img in buttons.items():
    r, c = row_col_map[name]
    x = (c + 0.5) * root.winfo_screenwidth() / 2
    y = (r + 0.5) * root.winfo_screenheight() / 2
    btn = tk.Button(root, image=img,
                    activebackground=BUTTON_ACTIVE_BG,
                    command=launch_map[name], relief="flat", borderwidth=0)
    btn_window = canvas.create_window(x, y, window=btn, anchor="center")
    btn_widgets[name] = btn

# ----------------- RUN APP -----------------
root.mainloop()
