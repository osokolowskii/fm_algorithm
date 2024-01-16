import pandas as pd
import json


class FMAlgorithm:
    team_file = 'ekstraklasa/pogon.html'

    positions_file = 'positions.json'
    # positions_file = 'positions_short.json'
    with open(positions_file, 'r') as f:
        positions = json.load(f)


    squad_rawdata_list = pd.read_html(team_file, header=0, encoding="utf-8", keep_default_na=False)

    squad_rawdata = squad_rawdata_list[0]

    limit_calculation_to_positions = False
    calculated_players = []

    def calculate_role_strenght(self, player):
        
        player_roles = {
            'Name': player['Name'],
            'Age': player['Age'],
            'Height': player['Height'],
            'Personality': player['Personality'],
            'Salary per month': player['Salary'].replace('\xa0', '.').replace('zl p/m', '')[:-1],
            'Value': player['Transfer Value'].replace('\xa0', '').replace('zl p/m', ''),
            'Young Status': player['Age'] < 23 and player['Nat'] == 'POL'
        }
        for role in self.positions:
            matching_role = [x for x in self.positions if x['RoleCode'] == role['RoleCode']]
            if not matching_role:
                break
            matching_role = matching_role[0]
            attrs_to_calculate = [(attr, matching_role[attr]) for attr in matching_role if attr not in ('RoleCode', 'Role') and matching_role[attr] > 0]
            role_strength = 0
            for attr in attrs_to_calculate:
                role_strength += player[attr[0]] * attr[1]
            player_roles[role['RoleCode']] = round(role_strength / len(attrs_to_calculate), 2)
        
        self.calculated_players.append(player_roles)

    def calculate_strength_for_team(self):
        for i in range(len(self.squad_rawdata)):
            self.calculate_role_strenght(self.squad_rawdata.iloc[i])
        return self.calculated_players
    
    def find_best_for_positions(self, n, positions=None):
        positions = positions or self.positions
        best_players = []
        for role in positions:
            best_players.append({role: [(player['Name'], player[role]) for player in sorted(self.calculated_players, key=lambda x: x[role], reverse=True)[:n]]})
        return best_players

algorithm = FMAlgorithm()
algorithm.calculate_strength_for_team()
for position in algorithm.find_best_for_positions(3, ['gkd', 'afa']):
    print(position)