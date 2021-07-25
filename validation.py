from typing import Dict, List
from models import SheetMapper, Locator, Rule, convert_to_python_expression
import logging

LOGGER = logging.getLogger(__name__)


def create_expression(
        rule: Rule,
        sheet_mappers: Dict[str, SheetMapper]
):

    locators = prepare_locators(rule)
    parsed_formula = rule.formula

    for expr, locator in locators.items():

        if not locator.sheet:
            locator.sheet = rule.get_base_sheet()

        if not locator.is_valid():
            raise Exception(f"{locator} for expression={expr} in rule={rule.id} is not valid")

        if locator.sheet not in sheet_mappers:
            raise Exception(f"No mapper registered for sheet=\"{locator.sheet}")

        sheet_mapper = sheet_mappers[locator.sheet]
        try:
            value = sheet_mapper.get_value(locator.row, locator.col)
            parsed_formula = parsed_formula.replace(expr, str(value))
        except Exception as e:
            raise Exception(f"Failed validating rule={rule.id} formula=\"{parsed_formula}\"", e)

    return convert_to_python_expression(parsed_formula)


def prepare_locators(rule: Rule):

    # Dont know if this can happen, but we need a warning here!
    if len(rule.restricted_rows) > 0 and len(rule.restricted_columns) > 0:
        raise Exception(f"Rule={rule.id} has both restricted rows and columns which is not supported right now")

    formular_locators = rule.extract_locators()
    if len(rule.restricted_rows) > 0:
        for restricted_col in rule.restricted_rows:
            for expr, locator in formular_locators.items():
                if not locator.row:
                    locator.row = restricted_col

    elif len(rule.restricted_columns) > 0:
        for restricted_col in rule.restricted_columns:
            for expr, locator in formular_locators.items():
                if not locator.col:
                    locator.col = restricted_col
                if not locator.sheet:
                    locator.sheet = rule.get_base_sheet()

    return formular_locators


def test_rules_with_mappers(
        rules: List[Rule],
        sheet_mappers: Dict[str, SheetMapper]
):

    for rule in rules:
        expression = create_expression(rule, sheet_mappers)
        callout(rule, expression)


def callout(rule: Rule, expression: str):
    ret = eval(expression)
    if ret:
        LOGGER.info(f"PASS: {rule.id}={rule.formula}")
    else:
        LOGGER.warning(f"FAIL: {rule.id}={rule.formula} -> {expression}")

