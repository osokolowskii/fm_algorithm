from collections import defaultdict

import json
import pandas as pd

class TransferEngine:
    def __init__(self, files_to_analyze):
        self.files_to_analyze = files_to_analyze


        self.position_with_roles_file = 'positions_with_roles.json'
        with open(self.position_with_roles_file, 'r') as f:
            self.positions_with_roles = json.load(f)

        self.position_dfs = defaultdict(lambda: pd.DataFrame())

        for file in self.files_to_analyze:
            df = pd.read_excel(file)
            self.position_dfs[file] = df

        self.merged_df = self.merge_dfs()

    def merge_dfs(self):
        merged_df = pd.concat(self.position_dfs.values(), ignore_index=True)
        # Define the number of columns for each sub-DataFrame
        num_cols_per_df = 3

        # Split the DataFrame into a list of smaller DataFrames
        sub_dfs = [merged_df.iloc[:, i:i+num_cols_per_df] for i in range(0, len(merged_df.columns), num_cols_per_df)]

        # Remove rows with all NaN values from each sub-DataFrame
        sub_dfs = [df.dropna(how='all') for df in sub_dfs]

        # Concatenate the sub-DataFrames back together
        merged_df = pd.concat(sub_dfs, axis=1)

        # Reset the index of the DataFrame
        merged_df = merged_df.reset_index(drop=True)

        return merged_df

    def get_targets(self, **params):
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

        if params.get('team'):
            if not params.get('strength'):
                raise ValueError('Please provide a strength value when specifying a team.')
            team_to_search = params['team']
            row_to_cut_from = self.find_team_row(new_df, team_to_search, params['strength'])
            new_df = new_df.iloc[:row_to_cut_from]

        if not params.get('role'):
            num_cols_per_df = 3
            sub_dfs = [new_df.iloc[:, i:i+num_cols_per_df] for i in range(0, len(new_df.columns), num_cols_per_df)]
            sub_dfs = [df.sort_values(by=df.columns[2]) for df in sub_dfs]
            new_df = pd.concat(sub_dfs, axis=1)
        else:
            new_df = new_df.sort_values(by=new_df.columns[2], ascending=False)

        return new_df
    
    def find_team_row(self, df, team, strength):
        found_str = 0
        for index, row in df.iterrows():
            if team in row.values:
                found_str += 1
                if found_str == strength or row.equals(df.iloc[-1]):
                    return index + 1

        return None

    
engine = TransferEngine(['role_rankings_2.xlsx', 'I_liga_polska_ranks.xlsx'])
# test_engine = TransferEngine(['ekstraklasa_reports/Pogoń_report.xlsx', 'ekstraklasa_reports/Lech_report.xlsx'])

print(engine.get_targets(position='GK', role='gkd', team='Łks', strength=1))