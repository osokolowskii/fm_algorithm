import PySimpleGUI as sg
from source.strength_algorithm import FMAlgorithm
from source.squad_analyzer import SquadAnalyzer
from source.transfer_engine import TransferEngine

def main():

    # Define the layout for the 'Strength Algorithm' tab
    strength_algorithm_layout = [
        [sg.Text('Whole League'), sg.Checkbox('', key='whole_league')],
        [sg.Text('Calculate Other Positions'), sg.Checkbox('', key='calculate_other_positions')],
        [sg.Text('League Directory'), sg.Input(key='league_directory'), sg.FolderBrowse()],
        [sg.Text('Team File'), sg.Input(key='team_file'), sg.FileBrowse()],
        [sg.Button('Run Strength Algorithm')]
    ]

    # Define the layout for the 'Prepare League Sheet' tab
    prepare_league_sheet_layout = [
        [sg.Text('League Directory'), sg.Input(key='league_directory_squad'), sg.FolderBrowse()],
        [sg.Button('Run Squad Analyzer')]
    ]

    # Define the layout for the 'Transfer Engine' tab
    transfer_engine_layout = [
        [sg.Text('Position'), sg.Input(key='position')],
        [sg.Text('Role'), sg.Input(key='role')],
        [sg.Text('Team'), sg.Input(key='team')],
        [sg.Text('Strength'), sg.Input(key='strength')],
        [sg.Text('Maximum Value'), sg.Input(key='maximum_value')],
        [sg.Text('Minimum Age'), sg.Input(key='minimum_age')],
        [sg.Text('Maximum Age'), sg.Input(key='maximum_age')],
        [sg.Text('Excel Reports Directory'), sg.Input(key='excel_reports_directory'), sg.FolderBrowse()],
        [sg.Button('Run Transfer Engine')]
    ]

    # Combine the layouts into a TabGroup
    layout = [
        [sg.TabGroup([
            [sg.Tab('Strength Algorithm', strength_algorithm_layout), 
            sg.Tab('Prepare League Sheet', prepare_league_sheet_layout),
            sg.Tab('Transfer Engine', transfer_engine_layout)]
        ])],
        [sg.Button('Exit')]
    ]

    # Create the window
    window = sg.Window('FM Algorithm', layout)

    # Event loop
    while True:
        event, values = window.read()

        # End program if user closes window or presses Exit
        if event == sg.WINDOW_CLOSED or event == 'Exit':
            break

        if event == 'Run Strength Algorithm':
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

        if event == 'Run Squad Analyzer':
            analyzer = SquadAnalyzer(league_dir=values['league_directory_squad'])
            analyzer.prepare_league_sheet()

        
        if event == 'Run Transfer Engine':
            engine = TransferEngine(values['excel_reports_directory'])
            targets = engine.get_targets(
                position=values['position'],
                role=values['role'],
                team=values['team'],
                strength=values['strength'],
                maximum_value=values['maximum_value'],
                minimum_age=values['minimum_age'],
                maximum_age=values['maximum_age'],
            )
            data = [list(row) for row in targets.values]
            headers = list(targets.columns)
            # Create a new window with a table displaying the DataFrame
            layout = [[sg.Table(values=data, headings=headers, display_row_numbers=True, auto_size_columns=True, num_rows=min(25, len(data)))]]
            window = sg.Window('Transfer Targets', layout)
            window.read()
            window.close()

    window.close()

if __name__ == '__main__':
    main()