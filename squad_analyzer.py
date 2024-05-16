import os
import pandas as pd

from collections import defaultdict

class SquadAnalyzer:
    def __init__(self, league_dir=False, team_excel_file=False, formation='4-4-2'):
        if team_excel_file:
            self.team_excel_file = team_excel_file
            self.squads = [self.get_squad()]
        else:
            self.league_dir = league_dir
            self.squads = self.get_squads_from_league()
        self.formation = formation

    def get_squads_from_league(self):
        for team in os.listdir(self.league_dir):
            squad_rawdata = pd.read_excel(team)
            self.squads.append(squad_rawdata)
        
    
    def get_squad(self):
        squad_rawdata = pd.read_excel(self.team_excel_file)
        self.squad_rawdata = squad_rawdata
    
    def get_formation_strength(self, formation_to_analyze):
        team_strength = {}
        for i, player in self.squad_rawdata.iterrows():
            team_strength[player['Name']] = player['Strength']
        return team_strength

    
squad_analyzer = SquadAnalyzer(team_excel_file='pogoń.xlsx', formation='4-2-3-1')
squad = squad_analyzer.get_squad()
print(squad_analyzer.get_formation_strength('4-2-3-1'))