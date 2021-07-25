from models import parse_to_rules, SheetMapper
import pandas as pd
import logging

from validation import test_rules_with_mappers

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

# Initialize the report mappers
test_sheet_mapper = SheetMapper("Report.xlsx", sheet_name="Eins", row_names_index=1, col_names_index=1)

# The report name to sheet mapper dictionary
sheet_mappers = {
    # The report name used rules
    "C 01.00": test_sheet_mapper
}

# Read the formulas file
df = pd.read_excel('EBA Validation Rules 2021-06-30.xlsx', sheet_name="v3.1.phase1")

# Filter by active rules
valid_rules = df[df["Deleted"] != "y"]

# Filter by rules that starts with the following report names
sheet_starts_with = ("C 01", "C 02", "C 03", "C 04", "C 05", "C 06")
valid_rules = valid_rules[valid_rules["T1"].str.startswith(sheet_starts_with)]

LOGGER.info(f"Parse {len(valid_rules)} valid rules of {len(df)}")

rules = parse_to_rules(valid_rules)

test_rules_with_mappers(rules, sheet_mappers)

