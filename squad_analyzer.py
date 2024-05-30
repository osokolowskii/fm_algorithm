import json
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

        
        self.position_with_roles_file = 'positions_with_roles.json'

        with open(self.position_with_roles_file, 'r') as f:
            self.positions_with_roles = json.load(f)

    def get_squads_from_league(self):
        squads = []
        for team in os.listdir(self.league_dir):
            team_path = os.path.join(self.league_dir, team)
            if os.path.isfile(team_path) and team_path.endswith(('.xlsx', '.xls')):
                squad_rawdata = pd.read_excel(team_path)
                squads.append({team.split('.')[0].capitalize(): squad_rawdata})
        return squads
        
        
    def get_squad(self):
        squad_rawdata = pd.read_excel(self.team_excel_file)
        self.squad_rawdata = squad_rawdata
    
    def rank_teams_in_role(self, role):
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
        # Create an empty DataFrame to store the results
        all_positions_df = pd.DataFrame()

        # Iterate through all positions
        for position in self.positions_with_roles:
            pos = position['Position']
            # Create a ranking for the given position
            position_df = self.rank_teams_in_position(position)

            # Add the position name to the column names
            position_df.columns = [f'{pos} {col}' for col in position_df.columns]

            # Add the ranking to the DataFrame
            all_positions_df = pd.concat([all_positions_df, position_df], axis=1)

        # Save the results to an Excel file
        all_positions_df.to_excel(f'{self.league_dir}_ranks.xlsx', index=False)



    # SECTION OF PREPARING TEAM REPORT

    def rank_positions_in_team(self, team):
        # Load team data
        team_squad = pd.read_excel(f'{self.league_dir}/{team}.xlsx')

        # Create an empty DataFrame to store the results
        team_report = pd.DataFrame()

        # Create a DataFrame to store player roles
        player_roles_df = pd.DataFrame()

        # Helper function to create a DataFrame for one position
        def create_position_df(pos, players, roles):
            # Create an empty DataFrame for this position
            pos_df = pd.DataFrame(columns=[pos, f'{pos} Ranking', f'{pos} Best Role'])

            # Iterate through all players
            for _, player in players.iterrows():
                # Check if the player has the given position
                if pos in player['Positions']:
                    # Calculate the strength for each role and save the strongest
                    best_role, best_strength = max(
                        ((role, player[role]) for role in roles),
                        key=lambda x: x[1]  # Compare strength, not role name
                    )

                    # Add the player to the DataFrame
                    pos_df = pos_df._append({
                        pos: player['Name'],
                        f'{pos} Ranking': best_strength,
                        f'{pos} Best Role': best_role
                    }, ignore_index=True)

                    # Add the player's role and strength to player_roles_df
                    player_roles_df[f'{player["Name"]} role'] = best_role
                    player_roles_df[f'{player["Name"]} strength'] = best_strength

            # Sort the DataFrame by Ranking in descending order
            pos_df = pos_df.sort_values(by=f'{pos} Ranking', ascending=False)

            # Reset the index of the DataFrame
            pos_df = pos_df.reset_index(drop=True)

            return pos_df

        # Iterate through all positions
        for position in self.positions_with_roles:
            pos = position['Position']
            alt = position.get('Alternative')

            # Create a DataFrame for the main position
            pos_df = create_position_df(pos, team_squad, position['Roles'])
            team_report = pd.concat([team_report, pos_df], axis=1)

            # If there is an alternative position, create a separate DataFrame for it
            if alt:
                alt_df = create_position_df(alt, team_squad, position['Roles'])
                team_report = pd.concat([team_report, alt_df], axis=1)

        # Save the team report to an Excel file
        os.makedirs(f'{self.league_dir}_reports', exist_ok=True)
        with pd.ExcelWriter(f'{self.league_dir}_reports/{team}_report.xlsx') as writer:
            team_report.to_excel(writer, sheet_name='Team Report', index=False)
            player_roles_df.to_excel(writer, sheet_name='Players', index=False)

    def rank_positions_in_all_teams(self):
        # Iterate through all teams in the league
        for squad_dict in self.squads:
            for team in squad_dict:
                self.rank_positions_in_team(team)

    def compare_teams(self, places=0, file_name='comparison.xlsx'):
        df = pd.DataFrame()

        position_dataframes = {}

        # Iterate through all positions
        for position in self.positions_with_roles:
            pos = position['Position']
            alt = position.get('Alternative')
            position_dataframes[pos] = pd.DataFrame()

            # Add headers for the main position
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
                # Load the team report into a DataFrame
                team_report = pd.read_excel(f'{self.league_dir}_reports/{file}')
                team_positions = team_report.columns[::3]
                team_name = file.replace('_report.xlsx', '')

                # Iterate through all positions in the team report
                for pos in team_positions:
                    # If a DataFrame for the position exists, add the data to it
                    if pos in position_dataframes:
                        position_data = team_report[[pos, f'{pos} Ranking', f'{pos} Best Role']].copy()
                        position_data = position_data.dropna()

                        # Add a column with the team name
                        position_data[f'{pos} Team'] = team_name

                        # If places is not zero, limit the number of players
                        if places != 0:
                            position_data = position_data.head(places)

                        position_dataframes[pos] = pd.concat([position_dataframes[pos], position_data])
                

        # Save the DataFrame to an Excel file
        for position_name, position_dataframe in position_dataframes.items():
            position_dataframes[position_name] = position_dataframe.sort_values(by=f'{position_name} Ranking', ascending=False)
        all_dataframes = [df.reset_index(drop=True) for pos, df in position_dataframes.items()]
        final_df = pd.concat(all_dataframes, axis=1)
        final_df.to_excel(f'{self.league_dir}_reports/{file_name}', index=False)


    
# squad_analyzer = SquadAnalyzer(team_excel_file='pogoń.xlsx')
squad_analyzer = SquadAnalyzer(league_dir='I_liga_polska')
# squad = squad_analyzer.get_squad()
squad_analyzer.analyze_all_positions()
# squad_analyzer.rank_positions_in_team('pogoń')
# squad_analyzer.rank_positions_in_all_teams()
# squad_analyzer.compare_teams()
