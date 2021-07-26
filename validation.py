import math
from typing import Dict, List
from models import SheetMapper, Rule, convert_to_python_expression, Locator
import logging
import copy

LOGGER = logging.getLogger(__name__)

# Generates python expressions to eval
# based on the rule formula and involved rows/columns
def generate_expression(rule: Rule, sheet_mappers: Dict[str, SheetMapper]):

    locators = rule.extract_locators()

    # For every generated base locator
    # Use it to satisfy the extracted locators
    for base_locator in generate_base_locator(rule, sheet_mappers):

        # But we need to create a copy of the extracted locators first
        final_locators = copy.deepcopy(locators)

        # Create a fresh copy of the formula each time
        parsed_formula = rule.formula

        # Iterate over all locators
        for expr, locator in final_locators.items():

            # Satisfy locator report by base locator
            if not locator.report:
                locator.report = rule.get_base_report()
                if not locator.report:
                    raise Exception(f"{locator} for expression={expr} in {rule} with base {base_locator} has no report reference")

            # Satisfy locator row by base locator
            if not locator.row:
                locator.row = base_locator.row
                if not locator.row:
                    raise Exception(f"{locator} for expression={expr} in {rule} with base {base_locator} has no row reference")

            # Satisfy locator column by base locator
            if not locator.col:
                locator.col = base_locator.col
                if not locator.col:
                    raise Exception(f"{locator} for expression={expr} in {rule} with base {base_locator} has no column reference")

            sheet_mapper = get_sheet_mapper(locator.report, sheet_mappers)
            try:
                value = sheet_mapper.get_value(locator.row, locator.col)
                if math.isnan(value):
                    value = "\"\""

                # Replace the locator expression by its actual value
                # Example: {Sheet, r001, c002} -> 13.13
                parsed_formula = parsed_formula.replace(expr, str(value))
            except Exception as e:
                raise Exception(f"Cannot create expression for {rule} formula=\"{parsed_formula}\"", e)

        # Generate python expression
        yield convert_to_python_expression(parsed_formula)


# Generates locators based on involved rows/columns
def generate_base_locator(rule: Rule, sheet_mappers: Dict[str, SheetMapper]):
    involved_row_count = len(rule.involved_rows)
    involved_col_count = len(rule.involved_columns)

    # Generate row/columns permutation
    if involved_row_count > 0 and involved_col_count > 0:
        for row in get_involved_rows(rule, sheet_mappers):
            for col in rule.involved_columns:
                locator = Locator()
                locator.row = row
                locator.col = col
                yield locator

    # Locator for rows only
    elif involved_row_count > 0:
        for row in get_involved_rows(rule, sheet_mappers):
            locator = Locator()
            locator.row = row
            yield locator

    # Locator for columns only
    elif involved_col_count > 0:
        for col in rule.involved_columns:
            locator = Locator()
            locator.col = col
            yield locator
    else:
        yield Locator()


# Get involved rows from a rule
# If the involved rows are "All", read all row ids from the sheet mapper
def get_involved_rows(rule: Rule, sheet_mappers: Dict[str, SheetMapper]):
    if rule.all_rows_involved():
        base_report = rule.get_base_report()
        if not base_report:
            raise Exception(f"{rule} has no involved base report")

        sheet_mapper = get_sheet_mapper(base_report, sheet_mappers)
        rows = sheet_mapper.get_all_rows().values
    else:
        rows = rule.involved_rows
    return rows


def get_sheet_mapper(report_name, sheet_mappers: Dict[str, SheetMapper]):
    if report_name not in sheet_mappers:
        raise Exception(f"No {SheetMapper.__class__.__name__} registered for report=\"{report_name}")
    return sheet_mappers[report_name]


# Tests all rules with data from the given sheets
def test_rules_with_mappers(rules: List[Rule], sheet_mappers: Dict[str, SheetMapper]):
    for rule in rules:
        for expression in generate_expression(rule, sheet_mappers):
            callout(rule, expression)


def callout(rule: Rule, expression: str):
    ret = eval(expression)
    if ret:
        LOGGER.info(f"PASS: {rule}: {rule.formula}")
    else:
        msg = f"{rule.severity.upper()}: {rule}: {rule.formula}, Python expression: {expression}"
        if rule.severity == Rule.SEVERITY_WARNING:
            LOGGER.warning(msg)
        else:
            LOGGER.error(msg)
