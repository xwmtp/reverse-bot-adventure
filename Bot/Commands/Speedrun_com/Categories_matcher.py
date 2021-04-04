from Bot.Config import Definitions
from Bot.Commands.Speedrun_com.Categories_info import download_src_category_info
from dataclasses import dataclass, field
from typing import List
import json
import re
import logging

class Categories_matcher:

    def __init__(self):
        self.src_categories_info = download_src_category_info()
        with open(Definitions.ROOT_DIR / 'Bot/Commands/Speedrun_com/Categories_names.json') as file:
            names_data = json.load(file)
        self.categories_nicknames = names_data

    def match(self, string):
        for category_names in self.categories_nicknames:
            match = self.match_on_full_category(string, category_names)
            if match:
                return self.match_found_category_with_src_info(match)

    def match_on_full_category(self, string, category):
        string = transform_query(string)
        string_remainder = self.match_on_category(string, category)
        if category["name"].lower() == "memes" and string_remainder is None:
            string_remainder = string
        if string_remainder is None:
            return

        if "vars" not in category:
            return self.Category_match(category["id"], category["name"])

        for var in category["vars"]:
            if self.match_on_variable(string_remainder, var):
                return self.Category_match(category["id"], category["name"], var["id"], var["name"])

        return self.Category_match(category["id"], category["name"])

    def match_on_category(self, string, category):
        string = transform_query(string)
        if string.startswith(category["name"].lower()):
            return string.replace(category["name"].lower(), '')
        for nickname in category["nicknames"]:
            if string.startswith(nickname.lower()):
                return string.replace(nickname.lower(), '')

    def match_on_variable(self, string, variable):
        string = transform_query(string)
        if string.startswith(variable["name"].lower()):
            return True
        for nickname in variable["nicknames"]:
            if string.startswith(nickname.lower()):
                return True
        return False

    @dataclass
    class Category_match:
        category_id: str
        category_name: str
        var_id: str = None
        var_name: str = None

    def match_found_category_with_src_info(self, match):
        for src_category_info in self.src_categories_info:
            if match.category_id == src_category_info.id:
                if match.category_name.lower() != src_category_info.name.lower():
                    logging.warning(
                        f"Name of SRC category {src_category_info.name} ({src_category_info.id}) is not equal to the name of matched category {match.category_name} {match.category_id}.")
                if match.var_id is None:
                    return src_category_info, src_category_info.get_default_var()

                for src_var in src_category_info.vars:
                    if match.var_id == src_var.id:
                        if match.var_name.lower() != src_var.name.lower():
                            logging.warning(
                                f"Name of SRC var {src_var.name} ({src_var.id}) of category {src_category_info.name} is not equal to the name of matched var {match.var_name} {match.category_id} of category {match.category_name}.")
                        return src_category_info, src_var
                logging.warning(f"Matched on var {match.var_name} ({match.var_id}) but did not find a matching var in the matched SRC category {src_category_info.name} ({src_category_info.id})")

    def print_categories_info_template(self):
        for category in self.src_categories_info:
            print(category.to_json_string() + ",")


def transform_query(query):
    query = query.lower()
    query = remove_most_special_characters(query)
    query = remove_extra_whitespace(query)
    return query

def remove_most_special_characters(string):
    # except for %, /
    return re.sub(r'[^A-Za-z0-9 %/]+', '', string)

def remove_extra_whitespace(string):
    return ' '.join(string.split())