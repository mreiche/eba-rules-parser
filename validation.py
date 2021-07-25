import math
from typing import Dict, List
from models import SheetMapper, Rule, convert_to_python_expression
import logging
import copy

LOGGER = logging.getLogger(__name__)


def create_expression(
        rule: Rule,
        sheet_mappers: Dict[str, SheetMapper]
):

    for locators in prepare_locators(rule):
        parsed_formula = rule.formula

        for expr, locator in locators.items():

            if not locator.report:
                locator.report = rule.get_base_sheet()

            if not locator.is_valid():
                raise Exception(f"{locator} for expression={expr} in {rule} is not valid")

            if locator.report not in sheet_mappers:
                raise Exception(f"No mapper registered for sheet=\"{locator.report}")

            sheet_mapper = sheet_mappers[locator.report]
            try:
                value = sheet_mapper.get_value(locator.row, locator.col)
                if math.isnan(value):
                    value = "\"\""

                parsed_formula = parsed_formula.replace(expr, str(value))
            except Exception as e:
                raise Exception(f"Failed validating {rule} formula=\"{parsed_formula}\"", e)

        yield convert_to_python_expression(parsed_formula)


def prepare_locators(rule: Rule):

    # Dont know if this can happen, but we need a warning here!
    if len(rule.involved_rows) > 0 and len(rule.involved_columns) > 0:
        raise Exception(f"{rule} has both restricted rows and columns which is not supported right now")

    locators = rule.extract_locators()

    # Yield locators with all involved rows
    if len(rule.involved_rows) > 0:
        for row in rule.involved_rows:
            final_locators = copy.deepcopy(locators)
            for expr, locator in final_locators.items():
                if not locator.row:
                    locator.row = row
            yield final_locators

    # Yield locators with all involved columns
    elif len(rule.involved_columns) > 0:
        for col in rule.involved_columns:
            final_locators = copy.deepcopy(locators)
            for expr, locator in final_locators.items():
                if not locator.col:
                    locator.col = col
            yield final_locators

    else:
        # Yield all locators
        yield locators


def test_rules_with_mappers(
        rules: List[Rule],
        sheet_mappers: Dict[str, SheetMapper]
):

    for rule in rules:
        for expression in create_expression(rule, sheet_mappers):
            callout(rule, expression)


def callout(rule: Rule, expression: str):
    ret = eval(expression)
    if ret:
        LOGGER.info(f"PASS: {rule}: {rule.formula}")
    else:
        LOGGER.warning(f"FAIL: {rule}: {rule.formula}, Python expression: {expression}")

