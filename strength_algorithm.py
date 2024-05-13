import os
import pandas as pd
import json

from collections import defaultdict


class FMAlgorithm:

    def __init__(self, whole_league=False):
        self.league_directory = 'ekstraklasa'

        self.positions_file = 'positions.json'
        self.position_with_roles_file = 'positions_with_roles.json'
        with open(self.positions_file, 'r') as f:
            self.positions = json.load(f)

        with open(self.position_with_roles_file, 'r') as f:
            self.positions_with_roles = json.load(f)


        if not whole_league:
            self.team_file = 'ekstraklasa/pogoń.html'
            self.squad_rawdata_list = pd.read_html(self.team_file, header=0, encoding="utf-8", keep_default_na=False)

            self.squad_rawdata = self.squad_rawdata_list[0]

        self.roles_for_all_positions = {item['Position']: item['Roles'] for item in self.positions_with_roles}
        self.roles_values = {item['RoleCode']: {k: v for k, v in item.items() if type(v) == int and v > 0} for item in self.positions}

    def get_positions_list(self, player_positions):
        positions_list = player_positions.replace(',', '/').split('/')
        all_positions = []
        if len(positions_list):
            for i, pos in enumerate(positions_list):
                if pos == 'GK':
                    return ['GK']
                if '(' not in pos:
                    all_sides = self.get_sides_for_position(positions_list, i)
                else:
                    all_sides = [pos[i] for i in range(pos.find('(')+1, pos.find(')'))]
                pos = pos.split('(')[0]
                all_positions.extend([f'{pos} ({side})' for side in all_sides])

        return all_positions
    
    def get_sides_for_position(self, player_positions, start_index):
        for i in range(start_index + 1, len(player_positions)):
            if '(' in player_positions[i]:
                index_of_side = player_positions[i].find('(')
                sides = list(player_positions[i][index_of_side+1:player_positions[i].find(')')])
                return sides
        return []

    
    def prepare_roles_for_player(self, player_positions):
        positions_list = self.get_positions_list(player_positions)
        return positions_list
    
    def calculate_strength_in_position(self, player, position):
        player_strength = defaultdict(lambda: 0)
        if 'DM' in position:
            position = 'DM (C)'
        roles_for_this_position = self.roles_for_all_positions[position.replace('  (', ' (').replace('(R)', '(L)')]
        for role in roles_for_this_position:
            for attribute in self.roles_values[role]:
                player_strength[role] += player[attribute] * self.roles_values[role][attribute]
            player_strength[role] = player_strength[role] / len(self.roles_values[role])
        return player_strength
    
    def calculate_strength_of_player(self, player):
        player_strength = defaultdict(lambda: 0)
        player_positions = self.get_positions_list(player['Position'])
        for position in player_positions:
            position = position.lstrip()
            position_strength = self.calculate_strength_in_position(player, position)
            for role, strength in position_strength.items():
                player_strength[role] += strength
        return player_strength
    
    def calculate_team_strength(self):
        team_strength = defaultdict(lambda: 0)
        for i, player in self.squad_rawdata.iterrows():
            player_strength = self.calculate_strength_of_player(player)
            team_strength[player['Name']] = player_strength
        return team_strength
    
    def save_team_strength(self, team_strength):
        data = [{'Name': name, **strengths} for name, strengths in team_strength.items()]
        df = pd.DataFrame(data)
        team_name = self.team_file.split('/')[-1].split('.')[0]
        df.to_excel(f'{team_name}.xlsx', index=False)

    def calculate_strength_of_league(self):
        for file in os.listdir(self.league_directory):
            if file.endswith('.html'):
                self.team_file = os.path.join(self.league_directory, file)
                self.squad_rawdata_list = pd.read_html(self.team_file, header=0, encoding="utf-8", keep_default_na=False)
                self.squad_rawdata = self.squad_rawdata_list[0]
                self.save_team_strength(self.calculate_team_strength())

    
    

algorithm = FMAlgorithm(whole_league=True)
# algorithm = FMAlgorithm()
# print(algorithm.save_team_strength(algorithm.calculate_team_strength()))
algorithm.calculate_strength_of_league()