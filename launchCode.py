import tkinter as tk
from PIL import Image, ImageTk
import os


# ----------------- CONFIG -----------------
ICON_SIZE = (200, 200)      # width, height in pixels
if os.path.exists("config.txt"):
    with open("config.txt", "r") as f:
        BG_IMAGE = f.read().strip()
else:
    BG_IMAGE = "imgs/Harumasa.png"

BUTTON_ACTIVE_BG = "#aaaaaa"
CONFIG_FILE = "config.txt"


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
bg_image_id = None
bg_animation_id = None
current_bg_type = None
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
    global bg_animation_id, current_bg_type

    if bg_animation_id:
        root.after_cancel(bg_animation_id)
        bg_animation_id = None

    canvas.delete("background")

    img = Image.open(path).convert("RGBA")
    img = img.resize(
        (root.winfo_screenwidth(), root.winfo_screenheight()),
        Image.Resampling.LANCZOS
    )

    bg = ImageTk.PhotoImage(img)
    canvas.img_ref = bg

    canvas.create_image(
        0, 0,
        anchor="nw",
        image=bg,
        tags="background"
    )

    canvas.tag_lower("background")
    current_bg_type = "static"





def play_gif_background(gif_path):
    global bg_animation_id, current_bg_type

    if bg_animation_id:
        root.after_cancel(bg_animation_id)
        bg_animation_id = None

    canvas.delete("background")

    gif = Image.open(gif_path)

    frames = []
    try:
        while True:
            frame = gif.copy().convert("RGBA")
            frame = frame.resize(
                (root.winfo_screenwidth(), root.winfo_screenheight()),
                Image.Resampling.LANCZOS
            )
            frames.append(ImageTk.PhotoImage(frame))
            gif.seek(gif.tell() + 1)
    except EOFError:
        pass

    image_id = canvas.create_image(
        0, 0,
        anchor="nw",
        image=frames[0],
        tags="background"
    )

    def animate(i=0):
        global bg_animation_id
        canvas.itemconfig(image_id, image=frames[i])
        canvas.img_ref = frames[i]
        bg_animation_id = root.after(16, animate, (i + 1) % len(frames))

    animate()
    canvas.tag_lower("background")
    current_bg_type = "gif"
    






# Decide what type of background to play
lower = BG_IMAGE.lower()

if lower.endswith(".mp4") or lower.endswith(".mov"):
    play_video_background(BG_IMAGE)
elif lower.endswith(".gif"):
    play_gif_background(BG_IMAGE)
else:
    play_static_background(BG_IMAGE)

from tkinter import filedialog

def change_background():
    global BG_IMAGE

    root.withdraw()
    root.update()

    file_path = filedialog.askopenfilename(
        title="Choose Background",
        filetypes=[
            ("Images", "*.png *.jpg *.jpeg *.gif"),
            ("All files", "*.*")
        ]
    )

    root.deiconify()
    root.attributes("-fullscreen", True)
    root.focus_force()

    if not file_path:
        return

    BG_IMAGE = file_path
    lower = file_path.lower()

    # 🔴 THIS WAS MISSING
    if lower.endswith(".gif"):
        play_gif_background(file_path)
    else:
        play_static_background(file_path)

    draw_buttons()
    draw_gear()

    # Save permanently
    with open(CONFIG_FILE, "w") as f:
        f.write(file_path)
    
    root.update_idletasks()

    canvas.tag_raise("buttons")
    canvas.tag_raise("gear")









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
gear_icon = Image.open("imgs/gear.png").convert("RGBA")
gear_icon = gear_icon.resize((48, 48), Image.Resampling.LANCZOS)
gear_icon = ImageTk.PhotoImage(gear_icon)


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
    btn = tk.Button(
        root,
        image=img,
        activebackground=BUTTON_ACTIVE_BG,
        command=launch_map[name],
        relief="flat",
        borderwidth=0
    )
    btn_widgets[name] = btn

gear_button = tk.Button(
    root,
    image=gear_icon,
    command=change_background,
    relief="flat",
    borderwidth=0,
    highlightthickness=0,
    bg="black",
    activebackground="black"
)


canvas.gear_ref = gear_icon 


def draw_buttons():
    canvas.delete("buttons")
    for name, btn in btn_widgets.items():
        r, c = row_col_map[name]
        x = (c + 0.5) * root.winfo_screenwidth() / 2
        y = (r + 0.5) * root.winfo_screenheight() / 2
        canvas.create_window(
            x, y,
            window=btn,
            anchor="center",
            tags="buttons"
        )

def draw_gear():
    canvas.delete("gear")
    canvas.create_window(
        root.winfo_screenwidth() - 40,
        root.winfo_screenheight() - 40,
        window=gear_button,
        anchor="se",
        tags="gear"
    )

lower = BG_IMAGE.lower()
if lower.endswith(".gif"):
    play_gif_background(BG_IMAGE)
else:
    play_static_background(BG_IMAGE)

draw_buttons()
draw_gear()

root.mainloop()
