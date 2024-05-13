import pandas as pd
import json

from collections import defaultdict


class FMAlgorithm:

    def __init__(self):
        self.team_file = 'ekstraklasa/pogoń.html'

        self.positions_file = 'positions.json'
        self.position_with_roles_file = 'positions_with_roles.json'
        # positions_file = 'positions_short.json'
        with open(self.positions_file, 'r') as f:
            self.positions = json.load(f)

        with open(self.position_with_roles_file, 'r') as f:
            self.positions_with_roles = json.load(f)


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
        roles_for_this_position = self.roles_for_all_positions[position]
        for role in roles_for_this_position:
            for attribute in self.roles_values[role]:
                player_strength[role] += player[attribute] * self.roles_values[role][attribute]
            print('Sum for role:' + role + ' is: ' + str(player_strength[role]) + ' for player: ' + player['Name'])
            player_strength[role] = player_strength[role] / len(self.roles_values[role])
            print('Average for role:' + role + ' is: ' + str(player_strength[role]) + ' for player: ' + player['Name'])
        return player_strength
    
    

algorithm = FMAlgorithm()
# print(algorithm.prepare_roles_for_player('DM / M (C) / AM (RL)'))
# print(algorithm.squad_rawdata)
# algorithm.calculate_strength_for_team()
print(algorithm.calculate_strength_in_position(algorithm.squad_rawdata.iloc[0], 'AM (L)'))
# for position in algorithm.find_best_for_positions(3, ['gkd', 'afa']):
#     print(position)