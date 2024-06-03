import PySimpleGUI as sg
from strength_algorithm import FMAlgorithm
from squad_analyzer import SquadAnalyzer
from transfer_engine import TransferEngine

def main():

    # Define the window's layout
    layout = [
        [sg.Text('Whole League'), sg.Checkbox('', key='whole_league')],
        [sg.Text('Calculate Other Positions'), sg.Checkbox('', key='calculate_other_positions')],
        [sg.Text('League Directory'), sg.Input(key='league_directory'), sg.FolderBrowse()],
        [sg.Text('Team File'), sg.Input(key='team_file'), sg.FileBrowse()],
        [sg.Button('Run'), sg.Button('Exit')]
    ]

    # Create the window
    window = sg.Window('FM Algorithm', layout)

    # Event loop
    while True:
        event, values = window.read()

        # End program if user closes window or presses Exit
        if event == sg.WINDOW_CLOSED or event == 'Exit':
            break

        if event == 'Run':
            algorithm = FMAlgorithm(
                whole_league=values['whole_league'],
                calculate_other_positions=values['calculate_other_positions'],
                league_directory=values['league_directory'],
                team_file=values['team_file']
            )
            if values['whole_league']:
                algorithm.calculate_strength_of_league()
            else:
                team_strength = algorithm.calculate_team_strength()
                algorithm.save_team_strength(team_strength)

    window.close()

if __name__ == '__main__':
    main()