from typing import List

from Bot.Config import Definitions
from Bot.Commands.Speedrun_com.Categories_SRC_info import download_src_category_info
from dataclasses import dataclass
import json
import re
import logging


class Categories_matcher:

    def __init__(self):
        self.src_categories_info = download_src_category_info()
        with open(Definitions.ROOT_DIR / 'Bot/Commands/Speedrun_com/Categories_names.json') as file:
            names_data = json.load(file)
        self.categories_nicknames = names_data
        # self.print_categories_info_template()

    def match(self, string):
        for category_names in self.categories_nicknames:
            if "collection" in category_names:
                match = self.match_on_category_or_subcategory(string, category_names)
            else:
                match = self.match_on_full_category(string, category_names)
            if match:
                return self.match_found_category_with_src_info(match)

    def match_on_full_category(self, string, category):
        string = transform_query(string)
        string_remainder = self.match_on_category(string, category)

        if string_remainder is None:
            return

        if "vars" not in category:
            return Category_match(category["id"], category["name"])

        matched_values = self.match_on_variables(string_remainder, category["vars"])
        return Category_match(category["id"], category["name"], matched_values)

    def match_on_category_or_subcategory(self, string, category):
        string = transform_query(string)
        string_remainder = self.match_on_category(string, category)

        if string_remainder is None:
            if "vars" not in category:
                return
            string_remainder = string

        if "vars" not in category:
            return Category_match(category["id"], category["name"])

        matched_values = self.match_on_variables(string_remainder, category["vars"])
        if len(matched_values) > 0:
            return Category_match(category["id"], category["name"], matched_values)

    def match_on_category(self, string, category):
        string = transform_query(string)
        if string.startswith(category["name"].lower()):
            return string.replace(category["name"].lower(), '')
        for nickname in category["nicknames"]:
            if string.startswith(nickname.lower()):
                return string.replace(nickname.lower(), '')

    def match_on_variables(self, string, variables):
        remainder = transform_query(string)
        value_matches = []
        while (True):
            new_remainder, value_matches = self._match_on_variables(remainder, variables, value_matches)
            if remainder == new_remainder:
                return value_matches
            remainder = new_remainder

    def _match_on_variables(self, remainder, variables, matches_so_far):
        for var in variables:
            for value in var["values"]:
                if var["id"] in [m.variable_id for m in matches_so_far]:
                    continue
                new_remainder = self.match_on_value(remainder, value)
                if new_remainder != None:
                    matches_so_far.append(Value_match(variable_id=var["id"],
                                                      value_id=value["id"],
                                                      value_name=value["name"]))
                    remainder = new_remainder
        return remainder, matches_so_far

    def match_on_value(self, string, value):
        string = transform_query(string)
        if string.startswith(value["name"].lower()):
            return string.replace(value["name"].lower(), '')
        for nickname in value["nicknames"]:
            if string.startswith(nickname.lower()):
                return string.replace(nickname.lower(), '')
        return

    # only return the found match if its id is actually present in the src info
    # log warning if there is an id match, but the names don't match (e.g. when a category has changed name on src)
    def match_found_category_with_src_info(self, match):
        if match.values is None:
            match.values = []

        for src_category_info in self.src_categories_info:
            if match.category_id == src_category_info.id:
                if match.category_name.lower() != src_category_info.name.lower():
                    logging.warning(
                        f"Name of SRC category {src_category_info.name} ({src_category_info.id}) is not equal to the name of matched category {match.category_name} {match.category_id}.")

                matched_src_values = []
                for src_var in src_category_info.vars:
                    src_value = self.find_src_value_in_match(src_var, match)
                    if src_value:
                        matched_src_values.append(src_value)
                    else:
                        matched_src_values.append(src_var.get_default_value())
                return src_category_info, matched_src_values


    def find_src_value_in_match(self, src_var, match):
        if src_var.id in [v.variable_id for v in match.values]:
            for src_value in src_var.values:
                if src_value.id in [v.value_id for v in match.values]:
                    return src_value

    def print_categories_info_template(self):
        for category in self.src_categories_info:
            print(category.to_json_string() + ",")


@dataclass
class Value_match:
    variable_id: str
    value_id: str
    value_name: str


@dataclass
class Category_match:
    category_id: str
    category_name: str
    values: List[Value_match] = None

    def has_matched_values(self):
        return isinstance(self.values, List) and len(self.values) > 0


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
