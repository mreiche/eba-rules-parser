from models import SheetMapper, Rule
import logging

from validation import prepare_locators, create_expression, callout

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

# Initialize the report mappers
test_sheet_mapper = SheetMapper("Report.xlsx", sheet_name="1", row_names_index=1, col_names_index=1)
assert 1337 == test_sheet_mapper.get_value("0100", "0030")
assert 26 == test_sheet_mapper.get_value("0200", "0040")

# The report name to sheet mapper dictionary
sheet_mappers = {
    # The report name used rules
    "TestSheet": test_sheet_mapper
}

# Create manual rules
rule = Rule("MeineRegel")
rule.involved_sheets.append("TestSheet")
rule.formula = "{r0100, c0030} + 3 = 1340"

locators = prepare_locators(rule)

expression = create_expression(rule, sheet_mappers)
ret = eval(expression)
callout(rule, ret)
