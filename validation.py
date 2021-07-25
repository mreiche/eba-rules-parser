import math
from typing import Dict, List
from models import SheetMapper, Rule, convert_to_python_expression, Locator
import logging
import copy

LOGGER = logging.getLogger(__name__)


def generate_expression(rule: Rule, sheet_mappers: Dict[str, SheetMapper]):

    locators = rule.extract_locators()

    for base_locator in generate_base_locator(rule, sheet_mappers):
        final_locators = copy.deepcopy(locators)

        parsed_formula = rule.formula

        for expr, locator in final_locators.items():

            if not locator.report:
                locator.report = rule.get_base_report()

            if not locator.row:
                locator.row = base_locator.row

            if not locator.col:
                locator.col = base_locator.col

            if not locator.is_valid():
                raise Exception(f"{locator} for expression={expr} in {rule} is not valid")

            sheet_mapper = get_sheet_mapper(locator.report, sheet_mappers)
            try:
                value = sheet_mapper.get_value(locator.row, locator.col)
                if math.isnan(value):
                    value = "\"\""

                parsed_formula = parsed_formula.replace(expr, str(value))
            except Exception as e:
                raise Exception(f"Failed validating {rule} formula=\"{parsed_formula}\"", e)

        yield convert_to_python_expression(parsed_formula)


def generate_base_locator(rule: Rule, sheet_mappers: Dict[str, SheetMapper]):
    involved_row_count = len(rule.involved_rows)
    involved_col_count = len(rule.involved_columns)

    # Generate row/col permutation
    if involved_row_count > 0 and involved_col_count > 0:
        for row in get_involved_rows(rule, sheet_mappers):
            for col in rule.involved_columns:
                locator = Locator()
                locator.row = row
                locator.col = col
                yield locator
    elif involved_row_count > 0:
        for row in get_involved_rows(rule, sheet_mappers):
            locator = Locator()
            locator.row = row
            yield locator
    elif involved_col_count > 0:
        for col in rule.involved_columns:
            locator = Locator()
            locator.col = col
            yield locator
    else:
        yield Locator()


def get_involved_rows(rule: Rule, sheet_mappers: Dict[str, SheetMapper]):
    if rule.all_rows_involved():
        base_report = rule.get_base_report()
        if not base_report:
            raise Exception(f"{rule} has no base report")

        sheet_mapper = get_sheet_mapper(base_report, sheet_mappers)
        rows = sheet_mapper.get_all_rows().values
    else:
        rows = rule.involved_rows
    return rows


def get_sheet_mapper(report_name, sheet_mappers: Dict[str, SheetMapper]):
    if report_name not in sheet_mappers:
        raise Exception(f"No {SheetMapper.__class__.__name__} registered for report=\"{report_name}")
    return sheet_mappers[report_name]


def test_rules_with_mappers(rules: List[Rule],sheet_mappers: Dict[str, SheetMapper]):
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
