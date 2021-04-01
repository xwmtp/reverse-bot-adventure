import logging

from Bot.Commands.Speedrun_com.Categories_info import download_category_info
from dataclasses import dataclass, field
from typing import List
import re


@dataclass
class Variable_names:
    id: str
    name: str
    alts: List[str]

    def match(self, string):
        string = transform_query(string)
        if string.startswith(self.name.lower()):
            return True
        for alt in self.alts:
            if string.startswith(alt.lower()):
                return True
        return False


@dataclass
class Category_names:
    id: str
    name: str
    alts: List[str]
    vars: List[Variable_names] = field(default_factory=list)

    def match(self, string):
        string = transform_query(string)
        string_remainder = self.match_category(string)
        if string_remainder != '' and not string_remainder:
            return
        matched_var = self.match_variables(string_remainder)
        if matched_var:
            return Category_match(self.id, self.name, matched_var.id, matched_var.name)
        else:
            return Category_match(self.id, self.name)

    def match_category(self, string):
        string = transform_query(string)
        if string.startswith(self.name.lower()):
            return string.replace(self.name.lower(), '')
        for alt in self.alts:
            if string.startswith(alt.lower()):
                return string.replace(alt.lower(), '')

    def match_variables(self, string):
        string = transform_query(string)
        for var in self.vars:
            if var.match(string):
                return var


@dataclass
class Category_match:
    category_id: str
    category_name: str
    var_id: str = None
    var_name: str = None


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


class Categories_matcher:

    def __init__(self):
        self.src_categories_info = download_category_info()
        self.categories_names = [
            Category_names(
                "q25g198d",
                "Any%",
                [
                    "Any"
                ]),
            Category_names(
                "q255jw2o",
                "100%",
                [
                    "Hundo"
                ]),
            Category_names(
                "zdnoz72q",
                "All Dungeons",
                [
                    "AD"
                ]),
            Category_names(
                "9d85yqdn",
                "GSR",
                [
                    "Ganondorf Source Requirement",
                    "Ganon Source Requirement",
                    "Ganondorf Source Requirements",
                    "Ganon Source Requirements",
                ]),
            Category_names(
                "jdrwr0k6",
                "MST",
                [
                    "Medallions Stones Trials",
                ]),
            Category_names(
                "zd35jnkn",
                "Glitchless", [
                    "Glitch less"
                ],
                [
                    Variable_names(
                        "gq79gxpl",
                        "Any%",
                        [
                            "Restricted",
                            "Any",
                            "Any% Restricted",
                            "Any Restricted",
                            "Restricted Any%",
                            "Restricted Any"
                        ]),
                    Variable_names(
                        "xqk98nd1",
                        "Any% Unrestricted",
                        [
                            "Unrestricted",
                            "Any Unrestricted",
                            "Unrestricted Any%"
                            "Bug Limit",
                            "Any% Bug Limit",
                            "Big Limit Any%"
                        ]),
                    Variable_names(
                        "p1259gk1",
                        "100% Unrestricted",
                        [
                            "100% Unrestricted",
                            "Hundo Unrestricted",
                            "Unrestricted 100%",
                            "Unrestricted Hundo",
                            "100% Bug Limit",
                            "Hundo Bug Limit",
                            "Bug Limit 100%",
                            "Bug Limit Hundo"
                        ]),
                    Variable_names(
                        "4qyyr34q",
                        "100%",
                        [
                            "100% Restricted",
                            "Restricted 100%",
                            "Hundo",
                            "Hundo Restricted",
                            "Restricted Hundo",
                        ])
                ]),
            Category_names(
                "z275w5k0",
                "Defeat Ganon",
                [
                    "Beat Ganon"
                ],
                [
                    Variable_names(
                        "5q85yy6q",
                        "No SRM",
                        [
                            "(No SRM)",
                            "No Stale Reference Manipulation",
                        ]),
                    Variable_names(
                        "4qy300dl",
                        "SRM",
                        [
                            "Stale Reference Manipulation",
                        ]),
                ]),
            Category_names(
                "xd1wj828",
                "No Wrong Warp",
                [
                    "No ww",
                    "Noww",
                    "No wws",
                    "No Wrong Warping",
                    "No Wrong Warps"
                ],
                [
                    Variable_names(
                        "0q5kyyvq",
                        "SRM", [
                            "Stale Reference Manipulation",
                        ]),
                    Variable_names(
                        "4lx3rrgl",
                        "No SRM",
                        [
                            "No Stale Reference Manipulation",
                        ]),
                ])
        ]

    def match(self, string):
        for category_names in self.categories_names:
            match = category_names.match(string)
            if match:
                print(match)
                return self.match_found_category_with_src_info(match)

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

