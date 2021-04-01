from xwillmarktheBot.Commands.Speedrun_stats.Speedrun_com.Category import Category
from xwillmarktheBot.Utils import *
import re

OOT_ID     = "j1l9qz1g"
OOT_EXT_ID = "76rkv4d8"

CONVERT_TERMS = {
    'item manipulation' : 'im',
    'ad' : 'all dungeons',
    'medallions, stones, trials' : 'mst',
    'medallions, stones, barrier' : 'msb',
    'no ww' : 'no wrong warp',
    'no source requirement' : 'nsr',
    'real time attack' : 'rta',
    'heart piece' : 'hp',
    'nms' : 'no major skips',
    'out of bounds' : 'oob',
    'reverse bottle adventure' : 'rba',
    'rdo' : 'reverse dungeon order',
    'hundo' : '100%',
    'dampe rta' : 'dampe hp rta',
    '37 keys' : '37 water temple keys',
    '37 water keys' : '37 water temple keys',
    'bug limit' : 'unrestricted',
    'glitchless unrestricted' : 'glitchless any% unrestricted'
}

CONVERT_CATS = {
    'glitchless unrestricted' : 'glitchless any% unrestricted '
}


class Category_matcher:

    def __init__(self):
        self.category_data = {}

    def match_category(self, str):
        sub_str = self.substitute_abbreviations(CONVERT_TERMS, str)
        # try exact matching
        match = self.find_exact_match(OOT_ID, sub_str)
        if not match:
            match = self.find_exact_match(OOT_EXT_ID, sub_str)
        # logging
        if match is None:
            logging.info(f"Couldn't find category {str}, searched for {sub_str}.")
        else:
            logging.debug(f"Found category match: {match.name}")
        return match

    def get_category_data(self, game_id):
        if game_id not in self.category_data.keys():
            self.category_data[game_id] = readjson(f'https://www.speedrun.com/api/v1/games/{game_id}/categories')['data']
        return self.category_data[game_id]

    def find_exact_match(self, category_id, str):
        logging.debug(f"Looking for matching category with {str} for game {category_id}")
        categories = self.get_category_data(category_id)
        for category in categories:
            name = category['name'].lower()
            category_names = self.get_category_alternatives(name)
            found_name = self.simple_match(str, category_names)
            if found_name is not None:
                logging.debug(f'Match on main catgeory: {found_name}')
                found_category = Category(category)
                remainder = str.replace(found_name + ' ', '')
                if len(remainder) > 0:
                    self.add_subcategory(remainder, found_category)
                return found_category

    def add_subcategory(self, str, category):
        """Find subcategory name in str and add to given category"""
        logging.debug(f'Looking up subcategories of {str} in {category.leaderboards.keys()} ')
        for subcategory in category.leaderboards.keys():
            subcat_names = self.get_category_alternatives(subcategory.lower(), is_subcat=True)
            found_subcat = self.simple_match(str, subcat_names)
            if found_subcat is not None:
                logging.debug(f'Found subcategory: {found_subcat}')
                category.selected_subcategory = subcategory
                break
        return category

    def get_category_alternatives(self, category, is_subcat = False):
        """Returns a list of possible alternative names for a category (i.e. bug limit for unrestricted)"""
        def delete_brackets(str):
            bracketless = re.sub(r"[\[\(].*?[\]\)]", '', str)
            spaceless = ' '.join(bracketless.split())
            return spaceless

        category_names = set([category]) # [] is necessary
        # add all alternatives
        category_names.add(delete_brackets(category))
        category_names.add(re.sub('[^\w ]','',category))
        if is_subcat:
            category_names.add(f'({category})')
        for name, sub_name in CONVERT_CATS.items():
            new_name = category.replace(name, sub_name)
            category_names.add(new_name)

        if len(category_names) > 1:
            logging.debug(f"Alternatives for categories found: {category_names}")

        return category_names

    def simple_match(self, word, list):
        """Return the closest match of a word with elements in a list.
        First tries exact match, then tries if any of the word starts with any of the elements."""
        logging.debug(f'Matching {word} with {list}')
        for elem in list:
            if word == elem:
                return elem
        for elem in list:
            if word.startswith(elem):
                return elem

    def substitute_abbreviations(self, dictionary, str):
        str = str.lower()
        # get rid of possible - surrounded by whitespaces
        str = re.sub(r" *- *", ' ', str)
        for term, sub_term in dictionary.items():
            # only replace if surrounded by non-alfanumeric or string start/end
            str = re.sub(r"(\W|^)" + term + r"(\W|$)", r"\g<1>" + sub_term + r"\g<2>", str)
        return str
