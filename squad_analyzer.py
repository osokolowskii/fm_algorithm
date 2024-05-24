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
            # Create a ranking for the given position
            position_df = self.rank_teams_in_position(position)

            # Add the ranking to the DataFrame
            all_positions_df = pd.concat([all_positions_df, position_df], axis=1)

        # Save the results to an Excel file
        all_positions_df.to_excel('role_rankings.xlsx', index=False)

    
# squad_analyzer = SquadAnalyzer(team_excel_file='pogoń.xlsx')
squad_analyzer = SquadAnalyzer(league_dir='ekstraklasa')
# squad = squad_analyzer.get_squad()
# print(squad_analyzer.get_formation_strength('4-2-3-1'))
# print(squad_analyzer.rank_teams_in_role('gkd'))
squad_analyzer.rank_teams_in_positions()