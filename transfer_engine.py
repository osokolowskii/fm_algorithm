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

        self.merged_dfs = self.merge_dfs()
        self.get_players()

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

    def get_players(self):
        print(self.merged_dfs)

    
# engine = TransferEngine(['role_rankings_2.xlsx'])
test_engine = TransferEngine(['ekstraklasa_reports/Pogoń_report.xlsx', 'ekstraklasa_reports/Lech_report.xlsx'])