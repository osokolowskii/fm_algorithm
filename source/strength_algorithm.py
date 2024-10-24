import os
import pandas as pd
import json

from collections import defaultdict

formations_dict = {
    'GK': ['GK'],
    'Defenders': ['D', 'WB'],
    'Midfielders': ['DM', 'M', 'AM'],
    'Attackers': ['ST', 'W']
}


class FMAlgorithm:

    def __init__(self, whole_league=False, calculate_other_positions=False, league_directory='ekstraklasa', team_file='ekstraklasa/pogoń.html', lang='en', save_attributes=False):
        """
        Initialize the FMAlgorithm.

        :param whole_league: Flag to indicate if we want to calculate strength of whole league.
        :param calculate_other_positions: Flag to indicate if we want to calculate strength for other positions than main.
        :param league_directory: Directory with league teams.
        :param team_file: File with team data.
        """
        self.league_directory = league_directory
        self.calculate_other_positions = calculate_other_positions
        self.lang = lang
        self.save_attributes = save_attributes

        self.positions_file = 'positions.json'
        self.position_with_roles_file = 'positions_with_roles.json'
        with open(self.positions_file, 'r') as f:
            self.positions = json.load(f)

        with open(self.position_with_roles_file, 'r') as f:
            self.positions_with_roles = json.load(f)


        if not whole_league:
            self.team_file = team_file
            self.squad_rawdata_list = pd.read_html(self.team_file, header=0, encoding="utf-8", keep_default_na=False)

            self.squad_rawdata = self.squad_rawdata_list[0]

        self.roles_for_all_positions = {item['Position']: item['Roles'] for item in self.positions_with_roles}
        self.roles_values = {item['RoleCode']: {k: v for k, v in item.items() if type(v) == int and v > 0} for item in self.positions}
        self.all_attributes = list(attr for attr in self.positions[0].keys() if attr not in ['Role', 'RoleCode'])

    def get_positions_list(self, player_positions):
        """
        Method to retrieve list of positions for player.

        :param player_positions: Player positions.

        :return: List of positions for player.
        """
        positions_list = player_positions.replace(',', '/').split('/')
        all_positions = []
        if len(positions_list):
            for i, pos in enumerate(positions_list):
                if pos == 'GK':
                    return ['GK']
                if pos == 'DM':
                    return ['DM (C)']
                if '(' not in pos:
                    all_sides = self.get_sides_for_position(positions_list, i)
                else:
                    all_sides = [pos[i] for i in range(pos.find('(')+1, pos.find(')'))]
                pos = pos.strip().replace('  ', ' ').split(' ')[0]
                all_positions.extend([f'{pos} ({side})' for side in all_sides])

        return all_positions
    
    def get_sides_for_position(self, player_positions, start_index):
        """
        Method to get sides for position.

        :param player_positions: List of player positions.
        :param start_index: Index of position to start from in player_positions.

        :return: List of sides for position.
        """
        for i in range(start_index + 1, len(player_positions)):
            if '(' in player_positions[i]:
                index_of_side = player_positions[i].find('(')
                sides = list(player_positions[i][index_of_side+1:player_positions[i].find(')')])
                return sides
        return []

    
    def prepare_roles_for_player(self, player_positions):
        """
        Method to prepare roles for player based on his positions.

        :param player_positions: Player positions.

        :return: List of roles for player.
        """
        positions_list = self.get_positions_list(player_positions)
        return positions_list
    
    def calculate_strength_in_position(self, player, position, sign=1):
        """
        Method to calculate strength of player in given position.
        
        :param player: Player data.
        :param position: Position to calculate strength for.
        :param sign: Sign to multiply the strength by. 1 for main position, -1 for other positions.
        """
        player_strength = defaultdict(lambda: 0)
        if 'DM' in position:
            position = 'DM (C)'
        roles_for_this_position = self.roles_for_all_positions[position.strip().replace('  (', ' (').replace('(R)', '(L)')]
        for role in roles_for_this_position:
            for attribute in self.roles_values[role]:
                player_strength[role] += player[attribute] * self.roles_values[role][attribute] * sign
            player_strength[role] = player_strength[role] / len(self.roles_values[role])
        return player_strength
    
    def calculate_strength_of_player(self, player):
        """
        Method to calculate strength of player in every role he can play.

        :param player: Player data.

        :return: Dictionary with player strength in every role.
        """
        player_strength = defaultdict(lambda: 0)
        player_positions = self.get_positions_list(player['Position'])

        positions_to_calculate = player_positions if not self.calculate_other_positions else self.roles_for_all_positions.keys()

        for position in positions_to_calculate:
            sign = 1 if position in player_positions else -1
            position_strength = self.calculate_strength_in_position(player, position, sign=sign)
            
            max_strength = 0
            max_strength_role = None

            for role, strength in position_strength.items():
                player_strength[role] = strength
                if (strength > max_strength and sign == 1) or (strength < max_strength and sign == -1):
                    max_strength = strength
                    max_strength_role = role if sign == 1 else f'({role})'

            player_strength[f'BestRole_{position}'] = max_strength_role

        player_strength.update({
            'Positions': player_positions,
            'Formations': self.get_formations_from_positions(player_positions),
            'Value': player['Transfer Value'],
            'Age': player['Age'],
            'Salary': player['Salary'],
        })

        if player['Club']:
            player_strength['Club'] = player['Club']

        if self.save_attributes:
            player_strength.update({attr: player[attr] for attr in self.all_attributes})

        return player_strength
    
    def get_formations_from_positions(self, player_positions):
        """
        Method to get formations (defence, midfield, attack) from player positions.

        :param player_positions: List of player positions.

        :return: Set of formations.
        """
        formations = []
        for pos in player_positions:
            pos_to_check = pos.split(' ')[0]
            formations.extend([key for key, value in formations_dict.items() if pos_to_check in value])
                
        return set(formations)
    
    def calculate_team_strength(self):
        """
        Method to calculate strength of every player in team.
        """
        team_strength = defaultdict(lambda: 0)
        for i, player in self.squad_rawdata.iterrows():
            team_strength[player['Name']] = self.calculate_strength_of_player(player)
        return team_strength
    
    def save_player_strengths(self, team_strength, sort_type='classic'):
        """
        Method to save player strengths to DataFrame. Then it can be saved to Excel file.

        :param team_strength: Dictionary with team strength.
        :param sort_type: Sorting method. Can be 'classic', 'separately', or 'absolute'.

        :return: DataFrame with player strengths.
        """
        player_dfs = []
        for player_name, player_strengths in team_strength.items():
            player_data = []
            for role, strength in player_strengths.items():
                if type(strength) == float:
                    player_data.append({
                        f"{player_name} role": role,
                        f"{player_name} strength": float(strength)
                    })
            player_df = pd.DataFrame(player_data)

            if sort_type == 'classic':
                # Sort without editing any values (20 > 10 > -8 > -18)
                player_df = player_df.sort_values(by=f"{player_name} strength", ascending=False)
            elif sort_type == 'separately':
                # Sort separately - positive values first and descending, then negative values ascending (20 > 10 > -18 > -8)
                player_df_positive = player_df[player_df[f"{player_name} strength"] >= 0].sort_values(by=f"{player_name} strength", ascending=False)
                player_df_negative = player_df[player_df[f"{player_name} strength"] < 0].sort_values(by=f"{player_name} strength")
                player_df = pd.concat([player_df_positive, player_df_negative])
            elif sort_type == 'absolute':
                # Sort separately with absolute values (20 > -18 > 10 > -8)
                player_df['AbsoluteStrength'] = player_df[f"{player_name} strength"].abs()
                player_df = player_df.sort_values(by='AbsoluteStrength', ascending=False).drop(columns=['AbsoluteStrength'])

            player_df = player_df.reset_index(drop=True)
            player_dfs.append(player_df)

        player_strength_df = pd.concat(player_dfs, axis=1)
        return player_strength_df

    def save_team_strength(self, team_strength):
        """
        Method to save team strength to Excel file.

        :param team_strength: Dictionary with team strength.
        """
        data = [{'Name': name, **strengths} for name, strengths in team_strength.items()]
        df = pd.DataFrame(data)

        # Sort columns
        cols = df.columns.tolist()
        cols.remove('Name')
        best_role_cols = [col for col in cols if 'BestRole' in col]
        other_cols = [col for col in cols if 'BestRole' not in col]
        cols = ['Name'] + sorted(best_role_cols) + sorted(other_cols)
        df = df[cols]

        player_strength_df = self.save_player_strengths(team_strength, sort_type='classic')

        team_name = self.team_file.split('.')[0]
        with pd.ExcelWriter(f'{team_name}.xlsx') as writer:
            df.to_excel(writer, sheet_name='Team Strength', index=False)
            player_strength_df.to_excel(writer, sheet_name='Player Strengths', index=False)

    def calculate_strength_of_league(self):
        """
        Method to calculate strength of every team in league.
        """
        for file in os.listdir(self.league_directory):
            if file.endswith('.html'):
                self.team_file = os.path.join(self.league_directory, file)
                self.squad_rawdata_list = pd.read_html(self.team_file, header=0, encoding="utf-8", keep_default_na=False)
                self.squad_rawdata = self.squad_rawdata_list[0]
                self.save_team_strength(self.calculate_team_strength())

            
algorithm = FMAlgorithm(
    whole_league=True,
    calculate_other_positions=False,
    league_directory='lbs',
    save_attributes=True
)
algorithm.calculate_strength_of_league()