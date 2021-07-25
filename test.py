from eba_rules import parse_to_rules

import pandas as pd

import logging

LOGGER = logging.getLogger(__name__)

# read by default 1st sheet of an excel file
df = pd.read_excel('EBA Validation Rules 2021-06-30.xlsx', sheet_name="v3.1.phase1")

valid_rules = df[df["Deleted"] != "y"]

sheet_starts_with = ("C 01", "C 02", "C 03", "C 04", "C 05", "C 06")

valid_rules = valid_rules[valid_rules["T1"].str.startswith(sheet_starts_with)]

LOGGER.info(f"Parse {len(valid_rules)} valid rules of {len(df)}")

rules = parse_to_rules(valid_rules)

print(rules)

rules[0].parse_formula()
