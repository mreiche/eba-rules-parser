from typing import List

import pandas as pd
import re

__all_sheets = {}

def parse_value(value: str):
    if isinstance(value, str):
        value = value.strip()
        if len(value) == 0:
            return None

        return value

        # if value == Rule.NAN:
        #     return None

    return None


def parse_to_rules(df: pd.DataFrame):

    rules: List[Rule] = []

    for index, row in df.iterrows():
        rule = Rule()
        rules.append(rule)
        for sheets_row in ["T1", "T2", "T3", "T4", "T5", "T6", "T7"]:
            value = parse_value(row[sheets_row])
            if value:
                rule.involved_sheets.append(value)

        for restriction_row in ["rows", "columns"]:
            restricted_list = getattr(rule, "restricted_"+restriction_row)
            value = parse_value(row[restriction_row])
            if value:
                value = value.lstrip("(").rstrip(")").strip()
                for value in value.split():
                    restricted_list.append(value)

        rule.formula = row["Formula"]

        # print(row)

    return rules


class Rule:
    ALL="All"
    NAN="Nan"

    def __init__(self):
        self.involved_sheets: List[str] = []
        self.restricted_rows: List[str] = []
        self.restricted_columns: List[str] = []
        self.formula = None
        self.locators = {}

    def parse_formula(self):
        locators = re.findall("{[^}]+}", self.formula)
        for locator_str in locators:
            locator = Locator()
            locator.parse(locator_str)
            self.locators[locator_str] = locator
        return self.locators



def get_sheet(name: str):
    if not __all_sheets[name]:
        __all_sheets[name] = pd.DataFrame()
    return __all_sheets[name]


class Locator:
    # {C 03.00, r0060, c0010}
    def parse(self, locator: str):
        locator = locator.lstrip("{").rstrip("}")
        parts = locator.split(",")
        for part in parts:
            part = part.strip()
            if part.startswith("r"):
                self.row = part.lstrip("r")
            elif part.startswith("c"):
                self.col = part.lstrip("c")
            else:
                self.sheet = part

    def __init__(self):
        self.sheet = None
        self.row = None
        self.col = None
