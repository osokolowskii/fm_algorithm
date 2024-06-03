import json
import os
import pandas as pd
from collections import defaultdict

class SquadAnalyzer:
    def __init__(self, league_dir=False, team_excel_file=False):
        """
        Initialize the SquadAnalyzer class.

        :param league_dir: The directory containing the league data.
        :param team_excel_file: The Excel file containing the team data.
        """
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

    def get_squad(self):
        """
        Get the squad from the team Excel file.

        :return: The squad data.
        """
        squad_rawdata = pd.read_excel(self.team_excel_file)
        self.squad_rawdata = squad_rawdata

    def rank_teams_in_role(self, role):
        """
        Rank teams based on player strength in a specific role.

        :param role: The role to rank teams in.
        :return: A list of teams ranked by player strength in the role.
        """
        roles_strength = []
        for squad_dict in self.squads:
            for team, squad in squad_dict.items():
                for i, player in squad.iterrows():
                    if player.get(role) and not pd.isna(player[role]):
                        roles_strength.append([team, player['Name'], player[role]])

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
            for i, (team, player, strength) in enumerate(role_ranking):
                result_df.loc[i, f'{role} Team'] = team
                result_df.loc[i, f'{role} Player'] = player
                result_df.loc[i, f'{role} Strength'] = strength

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

        all_positions_df.to_excel(f'{self.league_dir}_ranks.xlsx', index=False)

    def rank_positions_in_team(self, team):
        team_squad = pd.read_excel(f'{self.league_dir}/{team}.xlsx')
        team_report = pd.DataFrame()
        player_roles_df = pd.DataFrame()

        def create_position_df(pos, players, roles):
            pos_df = pd.DataFrame(columns=[pos, f'{pos} Ranking', f'{pos} Best Role'])
            for _, player in players.iterrows():
                if pos in player['Positions']:
                    if player['Name'] == 'Kacper Babral':
                        break
                    best_role, best_strength = max(
                        ((role, player[role]) for role in roles),
                        key=lambda x: x[1]
                    )
                    pos_df = pos_df._append({
                        pos: player['Name'],
                        f'{pos} Ranking': best_strength,
                        f'{pos} Best Role': best_role
                    }, ignore_index=True)
                    player_roles_df[f'{player["Name"]} role'] = best_role
                    player_roles_df[f'{player["Name"]} strength'] = best_strength
            pos_df = pos_df.sort_values(by=f'{pos} Ranking', ascending=False)
            pos_df = pos_df.reset_index(drop=True)
            return pos_df

        for position in self.positions_with_roles:
            pos = position['Position']
            alt = position.get('Alternative')
            pos_df = create_position_df(pos, team_squad, position['Roles'])
            team_report = pd.concat([team_report, pos_df], axis=1)
            if alt:
                alt_df = create_position_df(alt, team_squad, position['Roles'])
                team_report = pd.concat([team_report, alt_df], axis=1)

        os.makedirs(f'{self.league_dir}_reports', exist_ok=True)
        with pd.ExcelWriter(f'{self.league_dir}_reports/{team}_report.xlsx') as writer:
            team_report.to_excel(writer, sheet_name='Team Report', index=False)
            player_roles_df.to_excel(writer, sheet_name='Players', index=False)

    def rank_positions_in_all_teams(self):
        """
        Rank positions in all teams and save the team reports to Excel files.
        """
        for squad_dict in self.squads:
            for team in squad_dict:
                self.rank_positions_in_team(team)

    def compare_teams(self, places=0, file_name='comparison.xlsx'):
        """
        Compare teams based on player strength in different positions and save the comparison to an Excel file.

        :param places: The number of top players to include in the comparison.
        :param file_name: The name of the output Excel file.
        """
        df = pd.DataFrame()

        position_dataframes = {}

        for position in self.positions_with_roles:
            pos = position['Position']
            alt = position.get('Alternative')
            position_dataframes[pos] = pd.DataFrame()

            df[pos] = []
            df[f'{pos} Team'] = []
            df[f'{pos} Ranking'] = []
            df[f'{pos} Best Role'] = []

            # If there is an alternative position, add headers for it
            if alt:
                position_dataframes[alt] = pd.DataFrame()
                df[alt] = []
                df[f'{alt} Team'] = []
                df[f'{alt} Ranking'] = []
                df[f'{alt} Best Role'] = []

        for file in os.listdir(f'{self.league_dir}_reports'):
            if file.endswith('_report.xlsx'):
                team_report = pd.read_excel(f'{self.league_dir}_reports/{file}')
                team_positions = team_report.columns[::3]
                team_name = file.replace('_report.xlsx', '')

                for pos in team_positions:
                    if pos in position_dataframes:
                        position_data = team_report[[pos, f'{pos} Ranking', f'{pos} Best Role']].copy()
                        position_data = position_data.dropna()

                        position_data[f'{pos} Team'] = team_name

                        if places != 0:
                            position_data = position_data.head(places)

                        position_dataframes[pos] = pd.concat([position_dataframes[pos], position_data])

        # Save the DataFrame to an Excel file
        for position_name, position_dataframe in position_dataframes.items():
            position_dataframes[position_name] = position_dataframe.sort_values(by=f'{position_name} Ranking', ascending=False)
        all_dataframes = [df.reset_index(drop=True) for pos, df in position_dataframes.items()]
        final_df = pd.concat(all_dataframes, axis=1)
        final_df.to_excel(f'{self.league_dir}_reports/{file_name}', index=False)