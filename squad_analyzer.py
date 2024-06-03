import json
import os
import pandas as pd
from collections import defaultdict

class SquadAnalyzer:
    def __init__(self, league_dir=False, only_positive=True, particular_teams=False):
        """
        Initialize the SquadAnalyzer class.

        :param league_dir: The directory containing the league data.
        :param team_excel_file: The Excel file containing the team data.
        """
        self.squads = []
        self.only_positive = only_positive
        
        self.league_dir = league_dir
        self.squads = self.get_squads_from_league()

        self.position_with_roles_file = 'positions_with_roles.json'

        with open(self.position_with_roles_file, 'r') as f:
            self.positions_with_roles = json.load(f)

    def get_squads_from_league(self):
        """
        Get squads from the league directory.

        :return: A list of squads.
        """
        squads = []
        for team in os.listdir(self.league_dir):
            team_path = os.path.join(self.league_dir, team)
            if os.path.isfile(team_path) and team_path.endswith(('.xlsx', '.xls')):
                squad_rawdata = pd.read_excel(team_path)
                squads.append({team.split('.')[0].capitalize(): squad_rawdata})
        return squads

    def rank_teams_in_role(self, role):
        """
        Rank teams based on player strength in a specific role.

        :param role: The role to rank teams in.
        :return: A list of teams ranked by player strength in the role.
        """
        def player_to_add(player):
            conditions = [
                player.get(role),
                not pd.isna(player[role])
            ]
            
            if self.only_positive:
                conditions.append(player[role] > 0)
            
            return all(conditions)
        
        roles_strength = []
        
        for squad_dict in self.squads:
            for team, squad in squad_dict.items():
                roles_strength.extend([[team, player['Name'], player[role], player['Age'], player['Salary'], player['Value']] for _, player in squad.iterrows() if player_to_add(player)])

        # Sort the list by player strength in the role (second element in the list)
        roles_strength.sort(key=lambda x: x[2], reverse=True)

        return roles_strength

    def rank_teams_in_position(self, position):
        """
        Rank teams based on player strength in a specific position.

        :param position: The position to rank teams in.
        :return: A DataFrame with teams ranked by player strength in the position.
        """
        # Create an empty DataFrame to store the results
        result_df = pd.DataFrame()

        # Iterate through all roles in the given position
        for role in position['Roles']:
            # Create a ranking for the given role
            role_ranking = self.rank_teams_in_role(role)

            # Add the ranking to the DataFrame
            for i, (team, player, strength, age, salary, value) in enumerate(role_ranking):
                result_df.loc[i, f'{role} Team'] = team
                result_df.loc[i, f'{role} Player'] = player
                result_df.loc[i, f'{role} Strength'] = strength
                result_df.loc[i, f'{role} Age'] = age
                result_df.loc[i, f'{role} Salary'] = salary
                result_df.loc[i, f'{role} Value'] = value

        return result_df

    def analyze_all_positions(self):
        """
        Analyze all positions and save the results to an Excel file.
        """
        all_positions_df = pd.DataFrame()

        for position in self.positions_with_roles:
            pos = position['Position']
            position_df = self.rank_teams_in_position(position)

            position_df.columns = [f'{pos} {col}' for col in position_df.columns]

            all_positions_df = pd.concat([all_positions_df, position_df], axis=1)

        all_positions_df.to_excel(f'{self.league_dir}_report.xlsx', sheet_name='League Summarize', index=False)

squad_analyzer = SquadAnalyzer(league_dir='ekstraklasa', only_positive=False)
squad_analyzer.analyze_all_positions()