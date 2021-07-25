import math

from models import SheetMapper, Rule
import logging

from validation import test_rules_with_mappers

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

# Initialize the report mappers
sheet_mapper_one = SheetMapper("Report.xlsx", sheet_name="Eins", row_names_index=1, col_names_index=1)
sheet_mapper_two = SheetMapper("Report.xlsx", sheet_name="Zwei", row_names_index=1, col_names_index=1)
assert 1337 == sheet_mapper_one.get_value("0100", "0030")
assert 26 == sheet_mapper_one.get_value("0200", "0040")
assert 33 == sheet_mapper_two.get_value("0900", "0080")
assert math.isnan(sheet_mapper_two.get_value("0200", "0030"))


# The report name to sheet mapper dictionary
sheet_mappers = {
    # The report name used rules
    "TestSheet": sheet_mapper_one,
    "Report2": sheet_mapper_two
}

rules = []

# Create manual rules
rule = Rule("MeineRegel")
rule.involved_reports.append("TestSheet")
rule.formula = "{r0100, c0030} + 3 = 1340"
rules.append(rule)

rule = Rule("Andere Regel")
rule.formula = "-16 = {TestSheet, r0200, c0040} - {TestSheet, r0200, c0030}"
rules.append(rule)

rule = Rule("Rule using columns")
rule.involved_rows.extend(["0600", "0900"])
rule.involved_reports.append("TestSheet")
rule.formula = "{c0030} + {c0040} <= {c0080}"
rules.append(rule)

rule = Rule("Two sheets")
rule.involved_columns.append("0040")
rule.formula = "{Report2, r0300} > {TestSheet, r0800}"
rules.append(rule)

rule = Rule("Percent")
rule.formula = "1.2= 1 + 1 * 20%"
rules.append(rule)

rule = Rule("Empty")
rule.formula = "{Report2, r0200, c0030} = empty"
rules.append(rule)

rule = Rule("Not empty")
rule.formula = "{Report2, r0700, c0040} != empty"
rules.append(rule)

rule = Rule("If")
rule.involved_reports.append("TestSheet")
rule.involved_rows.extend(["0100", "0200"])
rule.formula = "if {c0030} != empty then {c0040} != empty"
rules.append(rule)

rule = Rule("Max")
rule.formula = " 3 != max(3,10)"
rules.append(rule)

rule = Rule("Fail with Warning")
rule.formula = "3 = 1"
rule.severity = Rule.SEVERITY_WARNING
rules.append(rule)

rule = Rule("Fail with Error")
rule.formula = "3 = 1"
rule.severity = Rule.SEVERITY_ERROR
rules.append(rule)

rule = Rule("Rows not empty")
rule.involved_reports.append("TestSheet")
rule.involved_rows.extend(["0400", "0500", "0600"])
rule.formula = "{c0030} != empty"
rules.append(rule)

rule = Rule("Cols have value")
rule.involved_reports.append("TestSheet")
rule.involved_columns.extend(["0030", "0040"])
rule.formula = "{r0600} >= 2"
rules.append(rule)

rule = Rule("Rows and cols not empty")
rule.involved_reports.append("TestSheet")
rule.involved_rows.extend(["0400", "0500", "0600"])
rule.involved_columns.extend(["0030"])
rule.formula = "{TestSheet} != empty"
rules.append(rule)

rule = Rule("All rows not empty")
rule.involved_reports.append("TestSheet")
rule.involved_rows.append(Rule.ALL)
rule.involved_columns.append("0080")
rule.formula = "{TestSheet} != empty"
rules.append(rule)

test_rules_with_mappers(rules, sheet_mappers)
