import json
import os
import pandas as pd

from collections import defaultdict

class SquadAnalyzer:
    def __init__(self, league_dir=False, team_excel_file=False):
        self.squads = []
        if team_excel_file:
            self.team_excel_file = team_excel_file
            self.squads = [self.get_squad()]
        else:
            self.league_dir = league_dir
            self.squads = self.get_squads_from_league()

        
        self.position_with_roles_file = 'positions_with_roles.json'

        with open(self.position_with_roles_file, 'r') as f:
            self.positions_with_roles = json.load(f)

    def get_squads_from_league(self):
        squads = []
        for team in os.listdir(self.league_dir):
            team_path = os.path.join(self.league_dir, team)
            if os.path.isfile(team_path) and team_path.endswith(('.xlsx', '.xls')):
                squad_rawdata = pd.read_excel(team_path)
                squads.append({team.split('.')[0].capitalize(): squad_rawdata})
        return squads
        
    
    def get_squad(self):
        squad_rawdata = pd.read_excel(self.team_excel_file)
        self.squad_rawdata = squad_rawdata
    
    def get_formation_strength(self, formation_to_analyze):
        # TO BE IMPLEMENTED
        team_strength = {}
        for i, player in self.squad_rawdata.iterrows():
            team_strength[player['Name']] = player['Strength']
        return team_strength
    
    def rank_teams_in_role(self, role):
        roles_strength = []
        for squad_dict in self.squads:
            for team, squad in squad_dict.items():
                for i, player in squad.iterrows():
                    if not pd.isna(player[role]):
                        roles_strength.append([team, player['Name'], player[role]])

        # Sortowanie listy według siły gracza w roli (drugi element listy)
        roles_strength.sort(key=lambda x: x[2], reverse=True)

        return roles_strength
    
    def rank_teams_in_position(self, position):
    # Create an empty DataFrame to store the results
        result_df = pd.DataFrame()

        # Iterate through all roles in the given position
        for role in position['Roles']:
            # Create a ranking for the given role
            role_ranking = self.rank_teams_in_role(role)

            # Add the ranking to the DataFrame
            for i, (team, player, strength) in enumerate(role_ranking):
                result_df.loc[i, f'{role} Team'] = team
                result_df.loc[i, f'{role} Player'] = player
                result_df.loc[i, f'{role} Strength'] = strength

        return result_df

    def analyze_all_positions(self):
        # Create an empty DataFrame to store the results
        all_positions_df = pd.DataFrame()

        # Iterate through all positions
        for position in self.positions_with_roles:
            pos = position['Position']
            # Create a ranking for the given position
            position_df = self.rank_teams_in_position(position)

            # Add the position name to the column names
            position_df.columns = [f'{pos} {col}' for col in position_df.columns]

            # Add the ranking to the DataFrame
            all_positions_df = pd.concat([all_positions_df, position_df], axis=1)

        # Save the results to an Excel file
        all_positions_df.to_excel('role_rankings_2.xlsx', index=False)


    # SECTION OF PREPARING TEAM REPORT

    def rank_positions_in_team(self, team):
        # Wczytaj dane drużyny
        team_squad = pd.read_excel(f'{self.league_dir}/{team}.xlsx')

        # Stwórz pusty DataFrame do przechowywania wyników
        team_report = pd.DataFrame()

        # Funkcja pomocnicza do tworzenia DataFrame dla jednej pozycji
        def create_position_df(pos, players, roles):
            # Stwórz pusty DataFrame dla tej pozycji
            pos_df = pd.DataFrame(columns=[pos, f'{pos} Ranking', f'{pos} Best Role'])

            # Przejdź przez wszystkich piłkarzy
            for _, player in players.iterrows():
                # Sprawdź, czy piłkarz ma daną pozycję
                if pos in player['Positions']:
                    # Oblicz siłę dla każdej roli i zapisz najmocniejszą
                    best_role, best_strength = max(
                        ((role, player[role]) for role in roles),
                        key=lambda x: x[1]  # Porównaj siłę, nie nazwę roli
                    )

                    # Dodaj piłkarza do DataFrame
                    pos_df = pos_df._append({
                        pos: player['Name'],
                        f'{pos} Ranking': best_strength,
                        f'{pos} Best Role': best_role
                    }, ignore_index=True)

            # Sort the DataFrame by Ranking in descending order
            pos_df = pos_df.sort_values(by=f'{pos} Ranking', ascending=False)

            # Reset the index of the DataFrame
            pos_df = pos_df.reset_index(drop=True)

            return pos_df

        # Przejdź przez wszystkie pozycje
        for position in self.positions_with_roles:
            pos = position['Position']
            alt = position.get('Alternative')

            # Stwórz DataFrame dla głównej pozycji
            pos_df = create_position_df(pos, team_squad, position['Roles'])
            team_report = pd.concat([team_report, pos_df], axis=1)

            # Jeśli istnieje alternatywna pozycja, stwórz dla niej osobny DataFrame
            if alt:
                alt_df = create_position_df(alt, team_squad, position['Roles'])
                team_report = pd.concat([team_report, alt_df], axis=1)

        # Zapisz raport drużyny do pliku Excela
        os.makedirs(f'{self.league_dir}_reports', exist_ok=True)
        team_report.to_excel(f'{self.league_dir}_reports/{team}_report.xlsx', index=False)

    def rank_positions_in_all_teams(self):
        # Przejdź przez wszystkie drużyny w lidze
        for squad_dict in self.squads:
            for team in squad_dict:
                self.rank_positions_in_team(team)

    def compare_teams(self, places=0, file_name='comparison.xlsx'):
        df = pd.DataFrame()

        position_dataframes = {}

        # Przejdź przez wszystkie pozycje
        for position in self.positions_with_roles:
            pos = position['Position']
            alt = position.get('Alternative')
            position_dataframes[pos] = pd.DataFrame()

            # Dodaj nagłówki dla głównej pozycji
            df[pos] = []
            df[f'{pos} Team'] = []
            df[f'{pos} Ranking'] = []
            df[f'{pos} Best Role'] = []

            # Jeśli istnieje alternatywna pozycja, dodaj dla niej nagłówki
            if alt:
                position_dataframes[alt] = pd.DataFrame()
                df[alt] = []
                df[f'{alt} Team'] = []
                df[f'{alt} Ranking'] = []
                df[f'{alt} Best Role'] = []

        for file in os.listdir(f'{self.league_dir}_reports'):
            if file.endswith('_report.xlsx'):
                # Wczytaj raport drużyny do DataFrame
                team_report = pd.read_excel(f'{self.league_dir}_reports/{file}')
                team_positions = team_report.columns[::3]
                team_name = file.replace('_report.xlsx', '')

                # Przejdź przez wszystkie pozycje w raporcie drużyny
                for pos in team_positions:
                    # Jeśli DataFrame dla pozycji istnieje, dodaj dane do niego
                    if pos in position_dataframes:
                        position_data = team_report[[pos, f'{pos} Ranking', f'{pos} Best Role']].copy()
                        position_data = position_data.dropna()

                        # Dodaj kolumnę z nazwą drużyny
                        position_data[f'{pos} Team'] = team_name

                        position_dataframes[pos] = pd.concat([position_dataframes[pos], position_data])
                

        # Zapisz DataFrame do pliku Excela
        for position_name, position_dataframe in position_dataframes.items():
            position_dataframes[position_name] = position_dataframe.sort_values(by=f'{position_name} Ranking', ascending=False)
        all_dataframes = [df.reset_index(drop=True) for pos, df in position_dataframes.items()]
        final_df = pd.concat(all_dataframes, axis=1)
        final_df.to_excel(f'{self.league_dir}_reports/{file_name}', index=False)

    def format_excel(self, file_name='comparison.xlsx'):
        # Wczytaj plik Excela
        df = pd.read_excel(f'{self.league_dir}_reports/{file_name}')

        # Zapisz DataFrame do pliku Excela
        with pd.ExcelWriter(f'{self.league_dir}_reports/{file_name}_formatted.xlsx', engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
            workbook = writer.book
            worksheet = writer.sheets['Sheet1']
            
            # Ustaw szerokość kolumn na podstawie długości tekstu
            for i, column in enumerate(df.columns):
                column_width = max(df[column].astype(str).map(len).max(), len(column))
                worksheet.set_column(i, i, column_width)

        # Zapisz DataFrame do pliku Excela
        df.to_excel(f'{self.league_dir}_reports/{file_name}_formatted.xlsx', index=False)

    
            # Szymon Jopek


    
# squad_analyzer = SquadAnalyzer(team_excel_file='pogoń.xlsx')
squad_analyzer = SquadAnalyzer(league_dir='ekstraklasa')
# squad = squad_analyzer.get_squad()
# print(squad_analyzer.get_formation_strength('4-2-3-1'))
# squad_analyzer.analyze_all_positions()
# squad_analyzer.rank_positions_in_team('pogoń')
# squad_analyzer.rank_positions_in_all_teams()
# squad_analyzer.compare_teams()
squad_analyzer.format_excel()