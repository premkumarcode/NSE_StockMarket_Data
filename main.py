import Scripts.DisplayGui as DG


def main():
    display_object = DG.DisplayGui()


if __name__ == '__main__':
    main()
#
#
# from tkinter import *
# from PIL import ImageFont
#
#
# def move():
#     if message.winfo_x() + message.move >= message.x_limit or message.winfo_x() + message.move < 0:
#         message.move = -message.move
#     message.place(x=message.winfo_x() + message.move)
#     message.after(message.delay, move)
#
#
# gui = Tk()
# gui.geometry('8000x100+1+600')
# width = gui.winfo_screenwidth()
# spacer = (" " * (int(width) // 6))
# print((int(width) // 6))
# gui.title('ALERTS')
# gui.config(bg='blue')
# # message = Label(gui, text='this is a demo')
# message = "Hello World"
# # message.config(fg='white', bg='blue', font=('times', '60'))
# message.x_limit = 2000
# message.move = 2
# message.delay = 5
# message.place(x=1)
# message.after(10, move)
# print(message)
# gui.mainloop()
#
# if __name__ == '__main__':
#     move()
