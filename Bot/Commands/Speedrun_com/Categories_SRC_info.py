from Bot.Commands.Speedrun_com.Leaderboard_data import download_leaderboard
from Bot.Utils import make_request
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
        categories_data = make_request(f"https://www.speedrun.com/api/v1/games/{game_id}/categories?embed=variables")
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
    for var_data in vars_data['data']:
        default_value_id = var_data['values']['default']
        values = _parse_to_value(var_data['values']['values'], var_data["id"])
        variables.append(Variable(var_data['name'], var_data['id'], values, default_value_id))
    return variables

def _parse_to_value(values_data, variable_id):
    values = []
    for value_id, value_data in values_data.items():
        values.append(
            Value(
                name=value_data['label'],
                id=value_id,
                variable_id=variable_id
            ))
    return values




@dataclass
class Value:
    name : str
    id : str
    variable_id : str

    def to_dict(self):
        return {"id" : self.id, "name" : self.name, "nicknames" : [""]}

@dataclass
class Variable:
    name: str
    id: str
    values: List[Value]
    default_value_id: str

    def get_default_value(self):
        return next(value for value in self.values if value.id == self.default_value_id)

    def to_dict(self):
        return {"id" : self.id, "values" : [value.to_dict() for value in self.values]}


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
