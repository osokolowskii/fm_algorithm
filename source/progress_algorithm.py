import pandas as pd
import os
from pathlib import Path

class ProgressAlgorithm:
    def __init__(self, directory_path, output_file, analyzed_files_record='analyzed_files.txt'):
        self.directory_path = directory_path
        self.output_file = output_file
        self.analyzed_files_record = analyzed_files_record
        self.analyzed_files = self.load_analyzed_files()

    def load_analyzed_files(self):
        if os.path.exists(self.analyzed_files_record):
            with open(self.analyzed_files_record, 'r') as file:
                return set(file.read().splitlines())
        return set()

    def save_analyzed_files(self):
        with open(self.analyzed_files_record, 'w') as file:
            file.write('\n'.join(self.analyzed_files))

    def read_excel_files(self):
        player_data = {}
        for file in Path(self.directory_path).glob('*.xlsx'):
            if file.name not in self.analyzed_files:
                df = pd.read_excel(file)
                for _, row in df.iterrows():
                    player = row['Name']
                    if player not in player_data:
                        player_data[player] = []
                    player_data[player].append(row)
                self.analyzed_files.add(file.name)
        self.save_analyzed_files()
        return player_data

    def compare_progress(self, player_data):
        progress_data = {}
        for player, data in player_data.items():
            if len(data) > 1:
                # Convert each row to a DataFrame, ensuring numeric types for calculation
                numeric_data = [pd.to_numeric(row, errors='coerce').fillna(0) for row in data]
                # Concatenate the list of DataFrames
                concatenated_data = pd.concat(numeric_data, axis=1).T
                # Now apply drop_duplicates, reset_index, and diff
                progress_data[player] = concatenated_data.drop_duplicates().reset_index(drop=True).diff().fillna(0)
        return progress_data

    def save_to_excel(self, progress_data):
        with pd.ExcelWriter(self.output_file) as writer:
            for player, data in progress_data.items():
                data.to_excel(writer, sheet_name=player[:31])

    def run(self):
        player_data = self.read_excel_files()
        progress_data = self.compare_progress(player_data)
        self.save_to_excel(progress_data)

if __name__ == "__main__":
    pa = ProgressAlgorithm('progress', 'progress_report.xlsx')
    pa.run()