from tkinter import *
from pathlib import Path
from Pl.Forms.selCurFrm import App


BASE_DIR = Path(__file__).resolve().parent

if __name__ == "__main__":
    screen = Tk()
    screen.geometry("%dx%d+%d+%d" % (600, 200, 500, 400))
    screen.title("Currency Converter")


    try:
        icon_png = BASE_DIR / "img" / "ic1.png"
        if icon_png.exists():
            screen.iconphoto(True, PhotoImage(file=str(icon_png)))
        else:
            icon_ico = BASE_DIR / "img" / "ic1.ico"
            if icon_ico.exists():
                screen.iconbitmap(str(icon_ico))
    except Exception as e:
        print("Icon load warning:", e)

        screen.resizable(False, False)

        img_path = BASE_DIR / "img" / "world1.png"
        print("IMG PATH:", img_path, "exists:",img_path.exists())
        img = PhotoImage(file=str(img_path))
        lblImage = Label(screen, image=img)
        lblImage.place(x=401, y=1)

        app = App(screen)

        screen.mainloop()