import pandas as pd
import json


class FMAlgorithm:
    team_file = 'ekstraklasa/pogon.html'

    positions_file = 'positions.json'
    position_with_roles_file = 'positions_with_roles.json'
    # positions_file = 'positions_short.json'
    with open(positions_file, 'r') as f:
        positions = json.load(f)

    with open(position_with_roles_file, 'r') as f:
        positions_with_roles = json.load(f)


    squad_rawdata_list = pd.read_html(team_file, header=0, encoding="utf-8", keep_default_na=False)

    squad_rawdata = squad_rawdata_list[0]

    limit_calculation_to_positions = False
    calculated_players = []

    # def prepare_roles_for_player(self, player_positions):
    #     roles = []

    #     # Rozdziela pozycje na podstawie przecinków i nawiasów
    #     positions = [pos.strip() for pos in player_positions.replace(")", "").split(",")]

    #     for pos in positions:
    #         # Dzieli pozycje na główne i opcjonalne (jeśli istnieją)
    #         main_position, *options = pos.split(" ")
    #         options = options[0].split("/") if options else []

    #         # Przeszukuje JSON
    #         for item in self.positions_with_roles:
    #             item_main_position, *item_options = item['Position'].replace(")", "").split(" ")
    #             item_options = item_options[0].split("/") if item_options else []

    #             # Dokładne sprawdzenie, czy pozycje główne są takie same
    #             if main_position == item_main_position.split(" ")[0]:
    #                 # Sprawdza wszystkie kombinacje opcji
    #                 if not options or any(opt in item_options for opt in options) or all(opt in item_options for opt in options):
    #                     roles.extend(item['Roles'])
    #                 elif 'Alternative' in item:
    #                     # Sprawdza alternatywne pozycje
    #                     alt_options = item['Alternative'].replace(")", "").split(" ")[1].split("/")
    #                     if any(opt in alt_options for opt in options) or all(opt in alt_options for opt in options):
    #                         roles.extend(item['Roles'])

    #     return roles

    def get_positions_list(self, player_positions):
        positions = player_positions.split('/')
        if positions != player_positions:
        for pos in positions:

    
    def prepare_roles_for_player(self, player_positions):
        positions_list = self.get_positions_list(player_positions)



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
print(algorithm.prepare_roles_for_player('M (C)'))
algorithm.calculate_strength_for_team()
# for position in algorithm.find_best_for_positions(3, ['gkd', 'afa']):
#     print(position)