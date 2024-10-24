import json
import os
import pandas as pd

from collections import defaultdict

class StrengthAlgorithm:
    def __init__(self, league_dir, **kwargs):
        """
        Constructor for StrengthAlgorithm class.

        Args:
            league_dir (str): Directory of league files.

        Optional Args:
            team_dir (str): Directory of team file. Default is False.
            lang (str): Language of the league. Default is 'en'.
            positions_file (str): File with positions. Default is 'positions.json'.
            roles_of_positions_file (str): File with roles of positions. Default is 'roles_of_positions.json'.
            player_analysis_scope (int): Scope of player analysis. It should be in range 0-3.
                0 means don't calculate any player specific analysis.
                1 means calculate player specific analysis for players in names_to_calculate list.
                2 means calculate player specific analysis for all players playing in teams in names_to_calculate list.
                3 means calculate player specific analysis for all players.
            names_to_calculate (list): List of names for which player specific analysis should be calculated.
                It can contain names of players or teams, depending on player_analysis_scope.

        Raises:
            ValueError: If lang is not 'en' or 'pl'.
            ValueError: If positions_file does not exist.
            ValueError: If positions_file is not a json file.
            ValueError: If roles_of_positions_file does not exist.
            ValueError: If roles_of_positions_file is not a json file.
            ValueError: If player_analysis_scope is not in range 0-3.
            ValueError: If player_analysis_scope is 1 or 2 and names_to_calculate is not provided or is empty.
        """
        self.validate_kwargs(kwargs)

        self.league_dir = "raw_files" + league_dir
        team_dir = kwargs.get("team_dir", False)
        self.team_dir = f'{league_dir}/{team_dir}' if team_dir else False
        self.lang = kwargs.get("lang", "en")

        self.positions_file = "config/" + kwargs.get("positions_file", "positions.json")
        self.roles_of_postions_file = "config/" + kwargs.get("roles_of_postions_file", "roles_of_positions.json")

        self.positions = self.load_positions()
        self.roles_of_positions = self.load_roles_of_positions()

        self.player_analysis_scope = kwargs.get("player_analysis_scope", 0)
        self.names_to_calculate = kwargs.get("names_to_calculate") if self.player_analysis_scope in (1, 2) else None

    def validate_kwargs(self, **kwargs):
        """
        Method for validating kwargs passed to constructor.
        """
        if "lang" in kwargs and kwargs["lang"] not in ("en", "pl"):
            raise ValueError("lang must be 'en' or 'pl'")
        
        file_paths = [path for path in ("positions_file", "roles_of_positions_file") if path in kwargs]
        for file_path in file_paths:
            if not os.path.isfile(kwargs[file_path]):
                raise ValueError(f"{file_path} file does not exist")
            if not kwargs[file_path].endswith(".json"):
                raise ValueError(f"{file_path} file must be a json file")
            
        if "player_analysis_scope" in kwargs and kwargs["player_analysis_scope"] not in range(4):
            raise ValueError("player_analysis_scope must be in range 0-4 (without 4)")
        if kwargs.get("player_analysis_scope") in (1, 2) and not kwargs.get("names_to_calculate"):
            raise ValueError("names_to_calculate must be passed and not be empty in kwargs when player_analysis_scope is 1 or 2")

    def load_file(self, file):
        """
        Method for loading file from path passed in parameter and returning it as a dictionary.
        """
        with open(file, "r") as f:
            return json.load(f)
        
    def load_positions(self):
        """
        Method for loading positions from positions_file.
        """
        return self.load_file(self.positions_file)
    
    def load_roles_of_positions(self):
        """
        Method for loading roles of positions from roles_of_positions_file.
        """
        return self.load_file(self.roles_of_postions_file)