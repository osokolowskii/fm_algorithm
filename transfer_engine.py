from collections import defaultdict

import json
import pandas as pd

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

class TransferEngine:
    def __init__(self, files_to_analyze):
        """
        Initialize the TransferEngine.

        :param files_to_analyze: Files to analyze.
        """
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
            num_cols_per_df = 3
            sub_dfs = [new_df.iloc[:, i:i+num_cols_per_df] for i in range(0, len(new_df.columns), num_cols_per_df)]
            sub_dfs = [df.sort_values(by=df.columns[2]) for df in sub_dfs]
            sub_dfs = [df.reset_index(drop=True) for df in sub_dfs]  # Reset the index of each DataFrame in sub_dfs
            new_df = pd.concat(sub_dfs, axis=1)
        else:
            new_df.sort_values(by=new_df.columns[2], inplace=True, ascending=False)
            new_df.reset_index(drop=True, inplace=True)

        if params.get('team'):
            if not params.get('strength'):
                raise ValueError('Please provide a strength value when specifying a team.')
            row_to_cut_from = self.find_team_row(new_df, params['team'], params['strength'])
            new_df = new_df.iloc[:row_to_cut_from]
            new_df = new_df.reset_index(drop=True)

        return new_df
    
    def find_team_row(self, df, team, strength):
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
    
    #TODO: write compare_players function. it will accept 2 player names and return a DataFrame with their stats.
    # It will compare them only in positions where they both play, and also attributes such as age, height, weight, salary and value.
    # It will output the DataFrame with the comparison of both players, for example -5 means that player 1 is better by 5 in that role.
    # It will also output the total difference in the last row of the DataFrame.