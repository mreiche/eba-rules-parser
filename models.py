from typing import List, Dict

import pandas as pd
import re


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
        rule = Rule(row["ID"])
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

    def is_valid(self):
        return self.sheet and self.row and self.col

    def __str__(self):
        return f"{self.__class__.__name__}(sheet={self.sheet}, row={self.row}, col={self.col})"


class Rule:
    ALL="All"
    NAN="Nan"

    def __init__(self, id: str):
        self.id = id
        self.involved_sheets: List[str] = []
        self.restricted_rows: List[str] = []
        self.restricted_columns: List[str] = []
        self.formula: str = None

    def extract_locators(self) -> Dict[str, Locator]:
        locator_dict = {}
        locators = re.findall("{[^}]+}", self.formula)
        for locator_str in locators:
            locator = Locator()
            locator.parse(locator_str)
            locator_dict[locator_str] = locator

        return locator_dict

    def get_base_sheet(self):
        return self.involved_sheets[0]


# Maps report sheets to rows and columns
class SheetMapper:
    def __init__(self,
                 file_path: str,
                 sheet_name: str,
                 row_names_index,
                 col_names_index
    ):
       # path_to_excel = pd.ExcelFile(file_path)
        self.df: pd.DataFrame = pd.read_excel(file_path, sheet_name=sheet_name, header=None, engine='openpyxl')
        self.row_series = self.df[row_names_index]
        self.col_series = self.df.iloc[col_names_index]
        self.col_names_index = col_names_index
        self.row_names_index = row_names_index
        self.file_path = file_path
        self.sheet_name = sheet_name

    def find_row_by_id(self, id_str: str) -> pd.Series:
        return self.row_series[self.row_series == id_str]

    def find_col_by_id(self, id_str: str) -> pd.Series:
        return self.col_series[self.col_series == id_str]

    def get_value(self, row_value: str, col_value: str):
        row = self.find_row_by_id(row_value)
        if row.empty:
            raise Exception(f"Cannot find row with value=\"{row_value}\" at column index={self.col_names_index} in sheet=\"{self.sheet_name}\" of file={self.file_path}")

        col = self.find_col_by_id(col_value)
        if col.empty:
            raise Exception(f"Cannot find column with value=\"{col_value}\" at row index={self.col_names_index} in sheet=\"{self.sheet_name}\" of file={self.file_path}")

        return self.df.iloc[row.index[0], col.index[0]]


def convert_to_python_expression(formula: str):
    formula = formula.replace("=", "==")
    return formula
