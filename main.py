from tkinter import *
from tkinter import filedialog
from tkinter import scrolledtext
from datetime import date
from tkinter import INSERT

from rdl import *

output_filename = 'Наряд.docx'

def clicked_input_file():
    input_file = filedialog.askopenfilename(filetypes=(("MS Word documents", "*.docx"), ("all files", "*.*")))
    input_file_txt.configure(text=f'{input_file}')
    btn_output_file['state'] = 'normal'
    # btn_input_file.config(text=input_file)

def clicked_output_file():
    res = '{output_file_txt.get()}'
    # output_filename.configure(text=res)
    parsing_docx(input_file_txt, res)


window = Tk()
window.title("RDL Parser")
window.geometry('600x400')

btn_input_file = Button(window, text="открыть наряд от диспетчера", width=25, command=clicked_input_file)
btn_input_file.place(x=5, y=5)
input_file_txt = Label(window, text='')
input_file_txt.place(x=200, y=8)

btn_output_file = Button(window, text="распарсить и сохранить наряд", width=25, command=clicked_output_file)
btn_output_file.place(x=5, y=40)
btn_output_file['state'] = 'disabled'
output_file_name = Label(window, text='Имя файла для сохранения:')
output_file_name.place(x=200, y=43)
fn = generate_file_name()
v = StringVar(window, value=fn)
output_file_name = Entry(window, width=35, textvariable=v)
output_file_name.place(x=370, y=43)
log_block = scrolledtext.ScrolledText(window, width=30, height=20)
log_block.place(x=5, y=70)



window.mainloop()
