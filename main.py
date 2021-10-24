import tkinter
from app import App

def update(app):
    app.canvas.get_tk_widget().grid(row=0, column=1)
    root.after(100, update, app)

if __name__ == '__main__':
    root = tkinter.Tk()
    app = App(root)

    while True:
        root.after(100, update, app)
        root.mainloop()