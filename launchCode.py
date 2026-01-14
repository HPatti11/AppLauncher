import tkinter as tk
from PIL import Image, ImageTk
import os
import json
from tkinter import filedialog
from tkinter import messagebox



# ----------------- CONFIG -----------------
ICON_SIZE = (120, 120)      # width, height in pixels
if os.path.exists("config.txt"):
    with open("config.txt", "r") as f:
        BG_IMAGE = f.read().strip()
else:
    BG_IMAGE = "imgs/Harumasa.png"

BUTTON_ACTIVE_BG = "#aaaaaa"
CONFIG_FILE = "config.txt"
APPS_FILE = "apps.json"

def load_apps():
    if os.path.exists(APPS_FILE):
        with open(APPS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_apps(apps):
    with open(APPS_FILE, "w") as f:
        json.dump(apps, f, indent=4)

apps = load_apps()


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
drag_data = {
    "item": None,
    "x": 0,
    "y": 0
}
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
    
        # Keep buttons and gear above the background
        canvas.tag_raise("buttons")
        canvas.tag_raise("gear")
    
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


    draw_gear()

    # Save permanently
    with open(CONFIG_FILE, "w") as f:
        f.write(file_path)
    
    root.update_idletasks()

    canvas.tag_raise("buttons")
    canvas.tag_raise("gear")


def add_new_app():
    global apps   # 🔥 MUST be first line

    app_path = filedialog.askopenfilename(
        title="Choose an App",
        initialdir="/Applications",
        filetypes=[("macOS Apps", "*.app")]
    )
    if not app_path:
        return

    icon_path = filedialog.askopenfilename(
        title="Choose an Icon",
        filetypes=[("Images", "*.png *.jpg *.jpeg")]
    )
    if not icon_path:
        return

    name = os.path.basename(app_path).replace(".app", "")

    apps[name] = {
        "path": app_path,
        "icon": icon_path
    }

    save_apps(apps)

    # 🔁 Reload + redraw
    apps = load_apps()
    rebuild_app_buttons()

def delete_app(app_name):
    global apps

    confirm = messagebox.askyesno(
        "Delete App",
        f"Delete '{app_name}'?"
    )

    if not confirm:
        return

    if app_name in apps:
        del apps[app_name]
        save_apps(apps)
        rebuild_app_buttons()

def on_drag_start(event):
    widget = event.widget

    # Find the canvas window that holds this widget
    for item in canvas.find_all():
        if canvas.type(item) == "window":
            if canvas.itemcget(item, "window") == str(widget):
                drag_data["item"] = item
                drag_data["x"] = event.x_root
                drag_data["y"] = event.y_root
                return


def on_drag_motion(event):
    if drag_data["item"] is None:
        return

    dx = event.x_root - drag_data["x"]
    dy = event.y_root - drag_data["y"]

    # Move the button on canvas
    canvas.move(drag_data["item"], dx, dy)

    # Keep it above the background
    canvas.lift(drag_data["item"])

    # Update drag coordinates
    drag_data["x"] = event.x_root
    drag_data["y"] = event.y_root


def on_drag_release(event):
    drag_data["item"] = None






# ----------------- LOAD ICONS -----------------
def load_icon(filename):
    try:
        img = Image.open(filename).convert("RGBA")
        img = img.resize(ICON_SIZE, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img)
    except FileNotFoundError:
        print(f"Warning: Icon not found: {filename}")
        return ImageTk.PhotoImage(Image.new("RGBA", ICON_SIZE, (128,128,128,255)))

chrome_logo   = load_icon("imgs/chrome.png")
facetime_logo = load_icon("imgs/facetime.png")
roblox_logo   = load_icon("imgs/roblox.png")
vscode_logo   = load_icon("imgs/vscode.png")
gear_icon = Image.open("imgs/gear.png").convert("RGBA")
gear_icon = gear_icon.resize((48, 48), Image.Resampling.LANCZOS)
gear_icon = ImageTk.PhotoImage(gear_icon)
plus_icon = Image.open("imgs/plus.png").convert("RGBA")
plus_icon = plus_icon.resize((48, 48), Image.Resampling.LANCZOS)
plus_icon = ImageTk.PhotoImage(plus_icon)


# ----------------- BUTTON GRID -----------------

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

add_button = tk.Button(
    root,
    image=plus_icon,
    command=add_new_app,
    relief="flat",
    borderwidth=0,
    bg="black",
    activebackground="black"
)
canvas.plus_ref = plus_icon


canvas.gear_ref = gear_icon 


def draw_gear():
    canvas.delete("gear")
    canvas.create_window(
        root.winfo_screenwidth() - 40,
        root.winfo_screenheight() - 40,
        window=gear_button,
        anchor="se",
        tags="gear"
    )
    canvas.create_window(
    root.winfo_screenwidth() - 100,
    root.winfo_screenheight() - 40,
    window=add_button,
    anchor="se",
    tags="gear"
)

def rebuild_app_buttons():
    canvas.delete("buttons")

    i = 0
    for name, data in apps.items():
        icon = load_icon(data["icon"])

        def launch(p=data["path"]):
            os.system(f"open '{p}' &")
            os._exit(0)

        btn = tk.Button(
            root,
            image=icon,
            command=launch,
            relief="flat",
            borderwidth=0
        )
        btn.image = icon

        # 🖱 RIGHT CLICK = DELETE
        btn.bind(
            "<Button-3>",
            lambda e, n=name: delete_app(n)
        )
        btn.bind("<ButtonPress-1>", on_drag_start)
        btn.bind("<B1-Motion>", on_drag_motion)
        btn.bind("<ButtonRelease-1>", on_drag_release)


        r = i // 4
        c = i % 4

        x = (c + 1) * root.winfo_screenwidth() / 5
        y = (r + 1) * root.winfo_screenheight() / 3

        canvas.create_window(
            x, y,
            window=btn,
            tags=("buttons", name)
        )

        i += 1

    canvas.tag_raise("buttons")
    


lower = BG_IMAGE.lower()
if lower.endswith(".gif"):
    play_gif_background(BG_IMAGE)
else:
    play_static_background(BG_IMAGE)

draw_gear()
rebuild_app_buttons()

root.mainloop()
