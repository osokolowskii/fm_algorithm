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

    def get_squads_from_league(self):
        squads = []
        for team in os.listdir(self.league_dir):
            team_path = os.path.join(self.league_dir, team)
            if os.path.isfile(team_path) and team_path.endswith(('.xlsx', '.xls')):
                squad_rawdata = pd.read_excel(team_path)
                squads.append({team.split('.')[0]: squad_rawdata})
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
                        roles_strength.append([team.capitalize(), player['Name'], player[role]])

        # Sortowanie listy według siły gracza w roli (drugi element listy)
        roles_strength.sort(key=lambda x: x[2], reverse=True)

        return roles_strength

    
# squad_analyzer = SquadAnalyzer(team_excel_file='pogoń.xlsx')
squad_analyzer = SquadAnalyzer(league_dir='ekstraklasa')
# squad = squad_analyzer.get_squad()
# print(squad_analyzer.get_formation_strength('4-2-3-1'))
print(squad_analyzer.rank_teams_in_role('gkd'))