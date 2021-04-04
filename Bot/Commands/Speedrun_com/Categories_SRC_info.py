from Bot.Commands.Speedrun_com.Leaderboard_data import download_leaderboard
from Bot.Utils import readjson
from dataclasses import dataclass
from typing import List
import logging
import json

GAME_IDs = {
    "oot": "j1l9qz1g",
    "ootextras" : "76rkv4d8"
}

def download_src_category_info():
    logging.info("Downloading categories info...")
    categories = []
    for game, game_id in GAME_IDs.items():
        categories_data = readjson(f"https://www.speedrun.com/api/v1/games/{game_id}/categories?embed=variables")
        if not 'data' in categories_data or categories_data['data'] == []:
            continue
        for category_data in categories_data['data']:
            if category_data['type'] == "per-game":
                categories.append(
                    Category(
                        name=category_data['name'],
                        id=category_data['id'],
                        game_id=game_id,
                        weblink=category_data['weblink'],
                        vars=_extract_src_variables_info(category_data['variables'])
                    ))
    logging.info("Completed downloading categories info.")
    return categories

def _extract_src_variables_info(vars_data):
    variables = []
    if not 'data' in vars_data or vars_data['data'] == []:
        return variables
    vars_data = vars_data['data'][0]
    default_var_id = vars_data['values']['default']
    for var_id, var_info in vars_data['values']['values'].items():
        variables.append(
            Variable(
                name=var_info['label'],
                id=var_id,
                group_id=vars_data['id'],
                default=var_id == default_var_id
            ))
    return variables


@dataclass
class Variable:
    name: str
    id: str
    group_id: str
    default: bool

    def to_dict(self):
        return {"id" : self.id, "name" : self.name, "nicknames" : [""]}


@dataclass
class Category:
    name: str
    id: str
    game_id: str
    weblink: str
    vars: List[Variable]

    def get_default_var(self):
        for var in self.vars:
            if var.default:
                return var

    def get_var(self, name):
        if len(self.vars) > 0:
            for var in self.vars:
                if var.name.lower() == name.lower():
                    return var
            return self.get_default_var()

    def get_leaderboard(self, var_name=''):
        var = self.get_var(var_name)
        return download_leaderboard(self, var)

    def to_json_string(self):
        dict = {"name" : self.name, "id" : self.id, "nicknames" : [""]}
        if len(self.vars) > 0:
            dict["vars"] = [var.to_dict() for var in self.vars]
        return json.dumps(dict, indent=2)
