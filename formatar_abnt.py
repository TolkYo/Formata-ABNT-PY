import pyautogui as pag
from tkinter import filedialog
import sys
import pyperclip
import time

# TEMPO ENTRE CADA AÇÃO
pag.PAUSE = 0.3

# FUNÇÕES IMPORTANTES
def break_page():
    pag.hotkey('ctrl', 'enter')

def copy_paste(texto):
    pyperclip.copy(texto)
    pag.hotkey('ctrl', 'shift', 'v')

def bold():
    pag.hotkey('ctrl', 'n')

def press_x_times(button, x):
    for i in range(0, x):
        pag.press(button)

def insert_file():
    #abre janela para seleção do arquivo word e recebe o caminho
    file_path = filedialog.askopenfilename(
        title="Selecione o arquivo Word",
        filetypes=[("Documentos Word", "*.docx *.doc")]
    )
    if not file_path: # parar o programa caso não selecione arquivo
        sys.exit()
    return file_path

def open_file(file_path):
    pag.hotkey('win', 'e')
    time.sleep(1)
    pag.hotkey('ctrl', 'l')
    copy_paste(file_path)
    pag.press('enter')
    time.sleep(3)

def justified_text():
    pag.press('ALT')
    pag.press('c')
    pag.press('u')
    pag.press('u')
def center_text():
    pag.press('ALT')
    pag.press('c')
    pag.press('a')
    pag.press('c')

def font_and_size():
    pag.hotkey('ctrl', 'shift', 'f')
    pag.write("Arial")
    pag.press('tab')
    pag.press('tab')
    pag.write("12")
    pag.press('enter')

def margin():
    pag.press('ALT')
    pag.press('q')
    pag.press('m')
    pag.press('a')
    pag.write("3")
    pag.press('tab')
    pag.write("2")
    pag.press('tab')
    pag.write("3")
    pag.press('tab')
    pag.write("2")
    pag.press('enter')
    time.sleep(0.8)

def line_spacing(): #1,5
    pag.press('ALT')
    pag.press('c')
    pag.press('p')
    pag.press('e')
    press_x_times('down', 2)
    pag.press('enter')

def do_cover():
    pag.hotkey('ctrl', 'home')
    break_page()
    pag.hotkey('ctrl', 'home')
    center_text()
    bold()
    pag.write("NOME DA INSTITUIÇÃO DE ENSINO")
    pag.press('enter')
    pag.write("NOME DO CURSO")
    press_x_times('enter', 3)
    pag.write("NOME DO ALUNO")
    press_x_times('enter', 12)
    pag.write("TITULO DO TRABALHO")
    pag.press('enter')
    bold()
    pag.write("Subtitulo (se houver)")
    press_x_times('enter', 11)
    bold()
    pag.write("Cidade da instituicao")
    pag.press('enter')
    pag.write("Ano de entrega")
    pag.press('enter')

def abstract():
    pag.write("RESUMO")
    bold()
    pag.press('enter')
    justified_text()
    pag.write("=lorem()")
    press_x_times('enter', 2)
    pag.write("Palavra-chave: ")
    break_page()
    center_text()
    bold()
    pag.write("ABSTRACT")
    bold()
    pag.press('enter')
    justified_text()
    pag.write("=lorem()")
    press_x_times('enter', 2)
    pag.write("Key word: ")

def summary():
    pag.press('ALT')
    pag.press('s')
    pag.press('s')
    press_x_times('enter', 2)

# MAIN -------------------
def main():
    file_path = insert_file()

    open_file(file_path)
    pag.click(x=850, y=461)
    pag.hotkey('ctrl', 't')
    justified_text()
    line_spacing()
    margin()
    do_cover()
    abstract()
    break_page()
    summary()
    pag.hotkey('ctrl', 't')
    font_and_size()
    pag.hotkey('ctrl', 'home')

if __name__ == "__main__":
    main()
