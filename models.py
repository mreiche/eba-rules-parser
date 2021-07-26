from typing import List, Dict

import pandas as pd
import re


def parse_value(value: str):
    if isinstance(value, str):
        value = value.strip()
        if len(value) > 0:
            return value

    return None


def parse_list_value(value: str):
    value = parse_value(value)
    if value:
        if value.startswith("(") and value.endswith(")"):
            value = value.lstrip("(").rstrip(")")
            values = []
            for part in value.split(","):
                values.append(part.strip())
            return values
        return [value]
    return []


def parse_to_rules(df: pd.DataFrame):
    rules: List[Rule] = []

    for index, row in df.iterrows():
        rule = Rule(row["ID"])
        rules.append(rule)
        for involved_report_col in ["T1", "T2", "T3", "T4", "T5", "T6", "T7"]:
            value = parse_value(row[involved_report_col])
            if value:
                rule.involved_reports.append(value)

        for involved_data_col in ["rows", "columns"]:
            target_list: List[str] = getattr(rule, "involved_" + involved_data_col)
            target_list.extend(parse_list_value(row[involved_data_col]))

        rule.formula = row["Formula"]
        rule.severity = row["Severity"]

    return rules


class Locator:
    ALL = "NNN"

    def __init__(self):
        self.report = None
        self.row = None
        self.col = None

    # {C 03.00, r0060, c0010}
    def parse(self, locator: str):
        locator = locator.lstrip("{").rstrip("}")
        parts = locator.split(",")
        for part in parts:
            values = parse_list_value(part)
            value = values[0]
            if value.startswith("r"):
                self.row = value.lstrip("r")
            elif value.startswith("c"):
                self.col = value.lstrip("c")
            else:
                self.report = value

    def __str__(self):
        return f"{self.__class__.__name__}(report={self.report}, row={self.row}, col={self.col})"


class Rule:
    ALL = "All"
    SEVERITY_WARNING = "Warning"
    SEVERITY_ERROR = "Error"

    def __init__(self, id: str):
        self.id = id
        self.involved_reports: List[str] = []
        self.involved_rows: List[str] = []
        self.involved_columns: List[str] = []
        self.formula = ""
        self.severity = Rule.SEVERITY_WARNING

    # Extract all locators from the formula
    def extract_locators(self):
        locator_dict: Dict[str, Locator] = {}
        locators = re.findall("{[^}]+}", self.formula)
        for locator_str in locators:
            locator = Locator()
            locator.parse(locator_str)
            locator_dict[locator_str] = locator

        return locator_dict

    def get_base_report(self):
        if len(self.involved_reports) > 0:
            return self.involved_reports[0]
        else:
            return None

    def all_rows_involved(self):
        if len(self.involved_rows) > 0 and self.involved_rows[0] == Rule.ALL:
            return True
        else:
            return False

    def __str__(self):
        return f"Rule(id={self.id})"


# Maps report sheets to rows and columns
class SheetMapper:
    def __init__(self,
                 file_path: str,
                 sheet_name: str,
                 row_names_index,
                 col_names_index
                 ):
        self.df: pd.DataFrame = pd.read_excel(file_path, sheet_name=sheet_name, header=None, engine='openpyxl')
        self.row_series = self.df[row_names_index] # blue in Report.xlsx
        self.col_series = self.df.iloc[col_names_index] # green in Report.xlsx
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
            raise Exception(
                f"Cannot find row with value=\"{row_value}\" at column index={self.col_names_index} in sheet=\"{self.sheet_name}\" of file=\"{self.file_path}\"")

        col = self.find_col_by_id(col_value)
        if col.empty:
            raise Exception(
                f"Cannot find column with value=\"{col_value}\" at row index={self.col_names_index} in sheet=\"{self.sheet_name}\" of file=\"{self.file_path}\"")

        return self.df.iloc[row.index[0], col.index[0]]

    def get_row_ids(self):
        return self.row_series[self.row_names_index+1:]


# Converts a formula to an evaluable python expression
def convert_to_python_expression(formula: str):
    # From: a = b
    # To: a == b
    formula = re.sub("([\\s\\d])=", "\\g<1>==", formula)

    # From: a%
    # To: (a/100)
    formula = re.sub("([\\d.]+)%", "(\\g<1>/100)", formula)

    # From: a = empty
    # To: a == ""
    formula = re.sub("empty", "\"\"", formula)

    # From: if a != empty then b > 30
    # To: b > 30 if a != "" else True
    if re.search("if\\s(?:.+)\\sthen", formula):
        parts = formula.split("then")
        formula = parts[1] + " " + parts[0] + " else True"

    return formula
