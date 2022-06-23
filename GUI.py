import threading
import traceback
import helpers as Helpers
import PySimpleGUI as sg
import subprocess

"""
    Demonstration of MENUS!
    How do menus work?  Like buttons is how.
    Check out the variable menu_def for a hint on how to 
    define menus
"""


def second_window():
    layout = [[sg.Text("New Window", key="new")]]
    window = sg.Window("Second Window", layout, modal=True)
    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        
    window.close()
    return window


def extract_from_csv_window():
    layout = [
        [sg.Text("Choose a *.csv file: ", pad=(1, 7))],
        [sg.Input(size=(50,10), pad=(1, 7)), sg.FileBrowse(file_types=(("CSV Files", "*.csv"),), pad=(1, 7))],
        [sg.Button("Submit", pad=(1, 7))],
        ]

    window = sg.Window('My File Browser', layout, size=(600,150))
    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        elif event == "Submit":
            print("=> Generating username set from the provided file dir...\n")
            try:
                username_set = Helpers.generate_username_set(layout[1][0].get(), players_id=False)
                # ! Important: we temporarily pickle the set
                Helpers.write_usernames(username_set)
                
            except Exception as e:
                tb = traceback.format_exc()
                sg.popup_error(f'ERROR:', e)
            break
    window.close()
    return "=> Extracted the usernames from the *.csv to txt & pkl files SUCCESFULLY...\n"

def main_menu():
    sg.theme('LightGreen')
    sg.set_options(element_padding=(0, 0))

    # ------ Menu Definition ------ #
    menu_def = [['&Help', '&About...'] ]

    # ------ GUI Defintion ------ #
    layout = [
        [sg.Menu(menu_def, tearoff=False, pad=(200, 1))],
        [sg.Column([[sg.Text('Choose the operation you need to do:', pad=(1, 7))]], justification='center')],
        [sg.Column([[sg.Button('Extract Username From A .csv File', pad=(1, 4))]], justification='center')],
        # [sg.Column([[sg.Button('Scrape games from txt', pad=(1, 4))]], justification='center')],
        [sg.Column([[sg.Button('Build Dataset', pad=(1, 4))]], justification='center')],
        [sg.Output((50,10))]
    ]

    window = sg.Window("Chess Players Evaluator",
                       layout,
                       default_element_size=(12, 1),
                       default_button_element_size=(12, 1))

    # ------ Loop & Process button menu choices ------ #
    while True:
        event, values = window.read()

        if event in (sg.WIN_CLOSED, 'Exit'):
            break
        # ------ Process menu choices ------ #
        if event == 'About...':
            window.disappear()
            sg.popup('About this program', 'Version 1.0',
                     'PySimpleGUI Version', sg.version,  grab_anywhere=True)
            window.reappear()

        elif event=='Extract Username From A .csv File':
            print('=> Extract Username From A .csv File\n')
            print(extract_from_csv_window())
            

        # elif event=='Scrape games from txt':
        #     print('=> Scrape games from txt\n')
        #     scrape_games_window()

        elif event=='Build Dataset':
            print('=> Build Dataset')
            second_window()
    window.close()
    

if __name__=='__main__':
    main_menu()