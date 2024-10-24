from collections import defaultdict

import os
import json
import pandas as pd

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

class TransferEngine:
    def __init__(self, directory_to_analyze):
        """
        Initialize the TransferEngine.

        :param files_to_analyze: Files to analyze.
        """
        self.directory_to_analyze = directory_to_analyze


        self.position_with_roles_file = 'positions_with_roles.json'
        with open(self.position_with_roles_file, 'r') as f:
            self.positions_with_roles = json.load(f)

        self.position_dfs = defaultdict(lambda: pd.DataFrame())

        for file in os.listdir(self.directory_to_analyze):
            if file.endswith(".xlsx"):
                df = pd.read_excel(os.path.join(self.directory_to_analyze, file))
                self.position_dfs[file] = df

        self.merged_df = self.merge_dfs()

    def merge_dfs(self):
        """
        Merge the DataFrames in self.position_dfs into a single DataFrame.

        Dataframes are at first splitted by columns of 3, because each 3 column is one role.
        We do not want to merge the DataFrames by rows, because we want to keep the roles separated.
        After splitting, we can remove NaN values from each sub-DataFrame and then concatenate them.

        :return: Merged DataFrame.
        """
        merged_df = pd.concat(self.position_dfs.values(), ignore_index=True)
        num_cols_per_df = 3
        sub_dfs = [merged_df.iloc[:, i:i+num_cols_per_df] for i in range(0, len(merged_df.columns), num_cols_per_df)]
        sub_dfs = [df.dropna(how='all') for df in sub_dfs]
        merged_df = pd.concat(sub_dfs, axis=1)
        merged_df.reset_index(drop=True, inplace=True)
        return merged_df

    def get_targets(self, **params):
        """
        Get the targets based on the provided parameters.

        :param params: Parameters to search for.

        :return: DataFrame with the targets.
        """
        target_df = self.merged_df.copy()

        if not params.get('position'):
            raise ValueError('Please provide a position to search for.')

        if params.get('role'):
            role_to_search = f"{params['position']} {params['role']}"
        else:
            role_to_search = params['position']

        role_columns = [col for col in target_df.columns if col.startswith(role_to_search)]
        new_df = target_df[role_columns]
        new_df = new_df.dropna()
        new_df.reset_index(drop=True, inplace=True)

        if not params.get('role'):
            num_cols_per_df = 6
            sub_dfs = [new_df.iloc[:, i:i+num_cols_per_df] for i in range(0, len(new_df.columns), num_cols_per_df)]
            sub_dfs = [self.apply_filters_on_df(df, params, role_to_search) for df in sub_dfs]
            sub_dfs = [df.sort_values(by=df.columns[2]) for df in sub_dfs]
            sub_dfs = [df.reset_index(drop=True) for df in sub_dfs]
            # new_df = pd.concat(sub_dfs, axis=1)
            new_df = self.prepare_position_df(sub_dfs)
        else:
            new_df = self.apply_filters_on_df(new_df, params, role_to_search)
            new_df.sort_values(by=new_df.columns[2], inplace=True, ascending=False)
            new_df.reset_index(drop=True, inplace=True)


        return new_df
    
    def find_row_to_cut_from(self, df, team, strength):
        """
        Method to find team row in the DataFrame. It is used, if we want to get n-th best player from team.

        :param df: DataFrame to search in.
        :param team: Team to search for.
        :param strength: Strength of the player to search for.

        :return: Index of the row in the DataFrame.
        """
        found_str = 0
        for index, row in df.iterrows():
            if team in row.values:
                found_str += 1
                if found_str == strength or row.equals(df.iloc[-1]):
                    return index + 1

        return None
    
    def apply_filters_on_df(self, df, params, role_to_search):
        new_df = df.copy()
        if not params.get('role'):
            role_to_search = df.columns[0].replace(' Team', '')
        if params.get('team'):
            if not params.get('strength'):
                raise ValueError('Please provide a strength value when specifying a team.')
            row_to_cut_from = self.find_row_to_cut_from(df, params['team'], params['strength'])
            new_df = new_df.iloc[:row_to_cut_from]
            new_df = new_df.reset_index(drop=True)

        if params.get('maximum_value'):
            def convert_value_to_float(value_range):
                if value_range == 'Not for Sale':
                    return 0
                if '-' in value_range:
                    max_value_str = value_range.split('-')[1].strip()
                    max_value = float(max_value_str.replace('\xa0zl', '').replace('.', '').replace('M', '000000').replace('K', '000').replace('B', '000000000').replace(',', ''))
                    return max_value

            new_df['max_value'] = new_df[f'{role_to_search} Value'].apply(convert_value_to_float)
            new_df.sort_values(by='max_value', ascending=False, inplace=True)
            new_df = new_df[new_df['max_value'] <= params['maximum_value']]
            new_df = new_df.reset_index(drop=True)
            new_df.drop(columns=['max_value'], inplace=True)

        if params.get('maximum_age'):
            new_df = new_df[new_df[f'{role_to_search} Age'] <= params['maximum_age']]
            new_df = new_df.reset_index(drop=True)

        if params.get('minimum_age'):
            new_df = new_df[new_df[f'{role_to_search} Age'] >= params['minimum_age']]
            new_df = new_df.reset_index(drop=True)

        if params.get('only_for_sale'):
            new_df = new_df[new_df[f'{role_to_search} Value'] != 'Not for Sale']
            new_df = new_df.reset_index(drop=True)

        if params.get('minimum_strength'):
            new_df = new_df[new_df[f'{role_to_search} Strength'] >= params['minimum_strength']]
            new_df = new_df.reset_index(drop=True)
        
        return new_df
    
    def prepare_position_df(self, sub_dfs):
        """
        Prepare the DataFrame with the positions.

        :param df: DataFrame to prepare.

        :return: Prepared DataFrame.
        """
        new_df = sub_dfs[0].copy()
        for df in sub_dfs[1:]:
            new_df = pd.concat([new_df, df.iloc[:, 2]], axis=1)

        # Change column names to only include the role for columns from the 7th to the end
        new_df.columns = list(new_df.columns[:6]) + [col.split(' Strength')[0].split(' ')[-1] for col in new_df.columns[6:]]

        # Select the columns to calculate max_strength
        max_strength_columns = [new_df.columns[2]] + list(new_df.columns[6:])

        new_df['average_strength'] = new_df[max_strength_columns].mean(axis=1)

        # Add the max_strength column
        new_df['max_strength'] = new_df[max_strength_columns].max(axis=1)

        # Add the max_strength_role column
        new_df['max_strength_role'] = new_df[max_strength_columns].idxmax(axis=1)

        return new_df
    
    def compare_players(self, player_1, player_2, limit_to=None):
        num_cols_per_df = 6
        sub_dfs = [self.merged_df.iloc[:, i:i+num_cols_per_df] for i in range(0, len(self.merged_df.columns), num_cols_per_df)]
        
        if limit_to is not None:
            players_dfs = [df for df in sub_dfs if player_1 in df.iloc[:, 1].values and player_2 in df.iloc[:, 1].values and df.columns[0].startswith(limit_to)]
        else:
            players_dfs = [df for df in sub_dfs if player_1 in df.iloc[:, 1].values and player_2 in df.iloc[:, 1].values]

        players_dfs = [df[df.iloc[:, 1].isin([player_1, player_2])] for df in players_dfs]

        new_df_headers = ["role", player_1, player_2, "difference"]
        new_df = pd.DataFrame(columns=new_df_headers)
        for df in players_dfs:
            player_1_row = df[df.iloc[:, 1] == player_1]
            player_2_row = df[df.iloc[:, 1] == player_2]
            if not player_1_row.empty and not player_2_row.empty:
                role = df.columns[0].split(' Team')[0]
                player_1_strength = player_1_row.iloc[0, 2]
                player_2_strength = player_2_row.iloc[0, 2]
                difference = player_1_strength - player_2_strength
                new_df = new_df._append(pd.Series([role, player_1_strength, player_2_strength, difference], index=new_df.columns), ignore_index=True)
        return new_df
    
    def compare_teams(self, team_1, team_2):
        num_cols_per_df = 6
        sub_dfs = [self.merged_df.iloc[:, i:i+num_cols_per_df] for i in range(0, len(self.merged_df.columns), num_cols_per_df)]
        team_dfs = [df for df in sub_dfs if team_1 in df.iloc[:, 0].values and team_2 in df.iloc[:, 0].values]
        team_dfs = [df[df.iloc[:, 0].isin([team_1, team_2])] for df in team_dfs]
    
transfer_engine = TransferEngine('lbr/')
# targets = transfer_engine.get_targets(
#     position='D (L)',
#     role='fbd',
#     # team='Pogoń',
#     # strength=2,
#     maximum_value=50000000,
#     # maximum_age=25,
#     # minimum_age=28,
#     minimum_strength=39,
# )
# print(targets)

comparison = transfer_engine.compare_players('Erik Expósito', 'Efthymis Koulouris')
print(comparison)
