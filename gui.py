from tkinter import *
import kv

window = Tk()
window.title("KV Downloader")
window.geometry('450x200')

lbl_u = Label(window, anchor=E, width=30, text="Username: ")
lbl_p = Label(window, anchor=E, width=30, text="Private Parts: ")
lbl_a = Label(window, anchor=E, width=30, text="Artist, eg. john-mayer:")
lbl_s = Label(window, anchor=E, width=30, text="Song, eg. born-and-raised:")
lbl_msg = Label(window, anchor=E, width=30, text="Ready")
lbl_result = Label(window, anchor=W, width=30, text=" ")

lbl_u.grid(column=0, row=0)
lbl_p.grid(column=0, row=2)
lbl_a.grid(column=0, row=4)
lbl_s.grid(column=0, row=6)
lbl_msg.grid(column=0, row=12)
lbl_result.grid(column=1, row=12)

txt_u = Entry(window,width=30)
txt_p = Entry(window,width=30)
txt_a = Entry(window,width=30)
txt_s = Entry(window,width=30)

txt_u.grid(column=1, row=0)
txt_p.grid(column=1, row=2)
txt_a.grid(column=1, row=4)
txt_s.grid(column=1, row=6)

def clicked():
    message = "Fetching "
    result = txt_s.get() + " by " + txt_a.get()
    lbl_msg.configure(text= message)
    lbl_result.configure(text=result)

btn = Button(window, text="Fetch Tracks", command=clicked) #command=kv.getTracks(txt_u,txt_p,txt_a,txt_s))
btn.grid(column=1, row=8)

window.mainloop()