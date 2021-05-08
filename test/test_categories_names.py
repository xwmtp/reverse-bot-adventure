from Bot.Commands.Speedrun_com.Categories_SRC_info import download_src_category_info
from Bot.Config import Definitions
import json
import unittest

def get_category_names():
    with open(Definitions.ROOT_DIR / 'Bot/Commands/Speedrun_com/Categories_names.json') as file:
        names_data = json.load(file)
    return names_data


class Test_categories_names(unittest.TestCase):
    src_category_info = download_src_category_info()
    category_names = get_category_names()

    def test_if_all_src_categories_have_defined_names(self):
        category_names_ids = [name["id"] for name in self.category_names]
        for src_category in self.src_category_info:
            self.assertIn(src_category.id, category_names_ids)

    def test_if_all_src_categories_have_same_name_as_category_names(self):
        for src_category in self.src_category_info:
            category_name = next(category for category in self.category_names if src_category.id == category["id"])
            self.assertEqual(src_category.name.lower(), category_name["name"].lower())

    def test_if_src_subcategory_has_same_name_as_category_sub_name(self):
        for src_category in self.src_category_info:
            if src_category.vars == []:
                continue
            category_name = next(category for category in self.category_names if src_category.id == category["id"])

            for src_var in src_category.vars:
                name_var = next(name_var for name_var in category_name['vars'] if name_var['id'] == src_var.id)
                for src_value in src_var.values:
                    name_value = next(name_value for name_value in name_var['values'] if name_value['id'] == src_value.id)
                    self.assertEqual(src_value.name.lower(), name_value["name"].lower())



if __name__ == '__main__':
    unittest.main()