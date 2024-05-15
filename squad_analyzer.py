import os
import pandas as pd

class SquadAnalyzer:
    def __init__(self, league_dir=False, team_excel_file=False):
        if not league_dir:
            self.team_excel_file = team_excel_file
            self.squads = [self.get_squad()]
        else:
            self.league_dir = league_dir
            self.squads = self.get_squads_from_leage()

    def get_squads_from_leage(self):
        for team in os.listdir(self.league_dir):
            squad_rawdata = pd.read_excel(team)
            self.squads.append(squad_rawdata)
        
    
    def get_squad(self):
        squad_rawdata = pd.read_excel(self.team_excel_file)
        return squad_rawdata
    
squad_analyzer = SquadAnalyzer(team_excel_file='pogoń.xlsx')
squad = squad_analyzer.get_squad()
print(squad)