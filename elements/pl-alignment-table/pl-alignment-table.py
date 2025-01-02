import html
import re
from typing import Any
import math
import chevron
import lxml.html
import prairielearn as pl
from typing_extensions import assert_never

WEIGHT_DEFAULT = 1
CORRECT_ANSWER_DEFAULT = None
LABEL_DEFAULT = None
PLACEHOLDER_DEFAULT = None
IGNORE_CASE_DEFAULT = False
SIZE_DEFAULT = 35
SHOW_HELP_TEXT_DEFAULT = True
SHOW_SCORE_DEFAULT = True
CELL_VALUE_DEFAULT = 0
CORRECT_ANSWER_DEFAULT = None
PENALTY_SCORE_DEFAULT = 1
ALIGNMENT_TYPE_DEFAULT = "global"

DP_TABLE_MUSTACHE_TEMPLATE_NAME = "pl-alignment-table.mustache"


def prepare(element_html: str, data: pl.QuestionData) -> None:
    """
    Prepare the data for the question.
    
    This function is called before the question is rendered.
    
    Args:
        element_html: The HTML of the element.
        data: The data object for the question.
        
    Returns:
        None
    """
    element = lxml.html.fragment_fromstring(element_html)
    required_attribs = ["answers-name"]
    optional_attribs = [
        "placeholder",
        "is-material",
        "path-only",
        "type",
    ]
    pl.check_attribs(element, required_attribs, optional_attribs)
    name = pl.get_string_attrib(element, "answers-name")
    pl.check_answers_names(data, name)

    v_string = "-" + data["params"].get("v")
    w_string = "-" + data["params"].get("w")
    num_rows = len(v_string)
    num_columns = len(w_string)

    # convert the correct answers to a dictionary of dictionaries
    if name in data["correct_answers"]:
        # split the string by newlines
        matrix, alignment, path, score = data["correct_answers"][name]
        # split each row by spaces
        data["correct_answers"][f"{name}_score"] = score
        for row_index in range(num_rows):
            for col_index in range(num_columns):
                data["correct_answers"][f"{name}_{row_index}_{col_index}"] = matrix[
                    row_index
                ][col_index]
                if [row_index, col_index] in path:
                    data["correct_answers"][f"{name}_{row_index}_{col_index}_p"] = True
        # reomve the original correct answers
        data["correct_answers"].pop(name)
    else:
        raise ValueError(f"Correct answers for {name} not found in data.")


def render(element_html: str, data: pl.QuestionData) -> str:
    """
    Render the question.
    
    This function is called to render the question.
    
    Args:
        element_html: The HTML of the element.
        data: The data object for the question. 
    
    Returns:
        str: The rendered question.
    """
    element = lxml.html.fragment_fromstring(element_html)
    name = pl.get_string_attrib(element, "answers-name")
    label = pl.get_string_attrib(element, "label", LABEL_DEFAULT)
    # Determine if the question is material (informational) or requires input
    is_material = pl.get_boolean_attrib(
        element, "is-material", False
    )  # Default to False if not specified
    path_only = pl.get_boolean_attrib(element, "path-only", False)
    placeholder = pl.get_string_attrib(element, "placeholder", PLACEHOLDER_DEFAULT)
    show_score = pl.get_boolean_attrib(element, "show-score", SHOW_SCORE_DEFAULT)

    raw_submitted_answer = data["raw_submitted_answers"].get(name)
    parse_error = data["format_errors"].get(name)
    score = data["partial_scores"].get(name, None)
    correct = False
    incorrect = False
    partial = False
    if score is not None:
        raw_score = score.get("score", None)
        if raw_score is not None:
            correct = raw_score == 1
            incorrect = raw_score == 0
            if not correct and not incorrect:
                partial = str(round(raw_score * 100, 2))

    feedback = data["partial_scores"].get(name, {"feedback": ""}).get("feedback", "")
    # Regular expression to capture i and j
    pattern = r"at row (\d+), column (\d+)"
    match = re.search(pattern, feedback)
    i_extracted = -1
    j_extracted = -1
    if match:
        i_extracted = int(match.group(1))  # The first captured group
        j_extracted = int(match.group(2))  # The second captured group

    v_string = "-" + data["params"].get("v")
    w_string = "-" + data["params"].get("w")
    num_rows = len(v_string)
    num_columns = len(w_string)

    columns = [{"w_letter": w} for w in w_string]
    rows = []

    prefill = pl.get_string_attrib(element, "prefill", CELL_VALUE_DEFAULT)

    for i, v_letter in enumerate(v_string):
        row = {"v_letter": v_letter, "data": []}  # First column letter from w
        for j, w_letter in enumerate(w_string):
            numerical_answer = ""
            boolean_answer = False
            if is_material:
                numerical_answer = pl.from_json(
                    data["correct_answers"].get(f"{name}_{i}_{j}", "")
                )
                boolean_answer = pl.from_json(
                    data["correct_answers"].get(f"{name}_{i}_{j}_p", False)
                )
            elif path_only:
                numerical_answer = pl.from_json(
                    data["correct_answers"].get(f"{name}_{i}_{j}", "")
                )
                boolean_answer = data["submitted_answers"].get(
                    f"{name}_{i}_{j}_p", False
                )
            else:
                numerical_answer = data["submitted_answers"].get(
                    f"{name}_{i}_{j}", prefill
                )
                boolean_answer = data["submitted_answers"].get(
                    f"{name}_{i}_{j}_p", False
                )
            row["data"].append(
                {
                    "col_index": j,
                    "row_index": i,
                    "value": numerical_answer,
                    "boolean": boolean_answer,
                    "correct": False,
                    "incorrect": False,
                    "input_error": data["format_errors"].get(f"{name}_{i}_{j}", None),
                    "first_incorrect": i == i_extracted and j == j_extracted,
                }
            )
        rows.append(row)

    correct_results = {}

    # Get template
    with open(DP_TABLE_MUSTACHE_TEMPLATE_NAME, "r", encoding="utf-8") as f:
        template = f.read()
    if data["panel"] == "question":
        info_template = "{{#format}}<p>{{{grading_text}}}</p>{{/format}}"
        grading_text = (
            "For each cell, click upper half of the cell to enter number for the upper half. Use arrow keys to quickly navigate through the table. <br />"
            "Use the <i class='bi bi-highlighter fa-xs'></i> button at the bottom of each cell to hightlight ONE path that represents the optimum alignment."
        )
        editable = data["editable"]
        info_params = {
            "format": True,
            "grading_text": grading_text,
        }
        info = chevron.render(info_template, info_params).strip()
        info = html.escape(info, quote=True)
        info = info.replace('"', "&quot;")
        show_help_text = pl.get_boolean_attrib(
            element, "show-help-text", SHOW_HELP_TEXT_DEFAULT
        )
        html_params = {
            "question": True,
            "name": name,
            "label": label,
            "editable": editable,
            "info": info,
            "placeholder": placeholder,
            "size": pl.get_integer_attrib(element, "size", SIZE_DEFAULT),
            "show_info": show_help_text,
            "uuid": pl.get_uuid(),
            "raw_submitted_answer": raw_submitted_answer,
            "parse_error": parse_error,
            "columns": columns,
            "rows": rows,
            "correct_results": correct_results,
            "is_material": is_material,
            "path_only": path_only,
            "correct": correct,
            "incorrect": incorrect,
            "partial": partial,
        }
        for row_index in range(num_rows):
            for col_index in range(num_columns):
                answer_name = f"{name}_{row_index}_{col_index}_p"
                if parse_error is None and answer_name in data["submitted_answers"]:
                    b_sub = data["submitted_answers"].get(answer_name, None)
                    if b_sub is None:
                        raise Exception(
                            f"submitted answer boolean is None for {answer_name}"
                        )
                    if isinstance(b_sub, bool):
                        b_sub = b_sub
                    else:
                        if b_sub in ["true", "True", "1"]:
                            b_sub = True
                        elif b_sub in ["false", "False", "0"]:
                            b_sub = False
                        else:
                            raise Exception(
                                f"submitted answer boolean is not a boolean for {answer_name}"
                            )
                    rows[row_index]["data"][col_index]["boolean"] = b_sub

        return chevron.render(template, html_params).strip()

    elif data["panel"] == "submission":
        html_params = {
            "submission": True,
            "name": name,
            "label": label,
            "parse_error": parse_error,
            "uuid": pl.get_uuid(),
            "columns": columns,
            "rows": rows,
            "correct": correct,
            "incorrect": incorrect,
            "partial": partial,
            "incorrect_message": feedback,
        }
        for row_index in range(num_rows):
            for col_index in range(num_columns):
                answer_name = f"{name}_{row_index}_{col_index}"
                if parse_error is None and answer_name in data["submitted_answers"]:
                    # Get the submitted answer for each cell
                    a_sub = data["submitted_answers"].get(answer_name, None)
                    if a_sub is None:
                        raise Exception(
                            f"submitted answer value is None for {answer_name}"
                        )
                    # Check if a_sub is a string before escaping
                    if isinstance(a_sub, str):
                        a_sub = pl.escape_unicode_string(a_sub)
                    else:
                        a_sub = str(
                            a_sub
                        )  # Convert non-string values to strings for rendering
                    rows[row_index]["data"][col_index]["value"] = a_sub

                    b_sub = data["submitted_answers"].get(
                        f"{name}_{row_index}_{col_index}_p", None
                    )
                    if b_sub is None:
                        raise Exception(
                            f"submitted answer boolean is None for {answer_name}"
                        )
                    if isinstance(b_sub, bool):
                        b_sub = b_sub
                    else:
                        if b_sub in ["true", "True", "1"]:
                            b_sub = True
                        elif b_sub in ["false", "False", "0"]:
                            b_sub = False
                        else:
                            raise Exception(
                                f"submitted answer boolean is not a boolean for {answer_name}"
                            )
                    rows[row_index]["data"][col_index]["boolean"] = b_sub
                else:
                    rows[row_index]["data"][col_index]["value"] = ""
                    rows[row_index]["data"][col_index]["boolean"] = False
                score = (
                    data["partial_scores"]
                    .get(answer_name, {"score": None})
                    .get("score", None)
                )
                if show_score and score is not None:
                    score_type, score_value = pl.determine_score_params(score)
                    html_params[score_type] = score_value
        html_params["error"] = html_params["parse_error"] or html_params.get(
            "missing_input", False
        )
        return chevron.render(template, html_params).strip()

    elif data["panel"] == "answer":
        html_params = {
            "answer": True,
            "name": name,
            "label": label,
            "columns": columns,
            "rows": rows,
            # "correct_results": correct_results,
        }
        for row_index in range(num_rows):
            for col_index in range(num_columns):
                answer_name = f"{name}_{row_index}_{col_index}"
                # Fetch the correct answer from the data
                correct_answer = pl.from_json(
                    data["correct_answers"].get(answer_name, None)
                )
                if correct_answer is None:
                    correct_answer = ""  # If no correct answer is found, leave it blank
                rows[row_index]["data"][col_index]["value"] = correct_answer

                path_name = f"{name}_{row_index}_{col_index}_p"
                # Fetch the correct answer from the data
                is_optimal = pl.from_json(data["correct_answers"].get(path_name, False))
                rows[row_index]["data"][col_index]["boolean"] = is_optimal
        return chevron.render(template, html_params).strip()
    assert_never(data["panel"])


def parse(element_html: str, data: pl.QuestionData) -> None:
    """
    Parse the submitted answers.
    
    This function is called to parse the submitted answers.
    
    Args:
        element_html: The HTML of the element.
        data: The data object for the question.
        
    Returns:
        None
    """
    element = lxml.html.fragment_fromstring(element_html)
    name = pl.get_string_attrib(element, "answers-name")

    # Check if the question is marked as material (informational)
    is_material = pl.get_boolean_attrib(element, "is-material", False)

    # If it's material, skip grading
    if is_material:
        return

    w_string = "-" + data["params"].get("w")
    v_string = "-" + data["params"].get("v")
    num_rows = len(v_string)
    num_columns = len(w_string)

    for row_index in range(num_rows):
        for col_index in range(num_columns):
            answer_name = f"{name}_{row_index}_{col_index}"
            a_sub = data["submitted_answers"].get(answer_name, None)

            if a_sub is None:
                data["format_errors"][name] = "No submitted answer."
                data["submitted_answers"][answer_name] = None
            else:
                try:
                    # Attempt to convert the submitted answer to a float
                    a_sub = float(a_sub)
                    data["submitted_answers"][answer_name] = pl.to_json(a_sub)
                except ValueError:
                    data["format_errors"][
                        name
                    ] = "Invalid format. Please enter a valid number."
                    data["submitted_answers"][answer_name] = None

            answer_name = f"{name}_{row_index}_{col_index}_p"
            a_sub = data["submitted_answers"].get(answer_name, None)
            if a_sub is None:
                data["format_errors"][name] = "No submitted answer."
                data["submitted_answers"][answer_name] = None
            else:
                if a_sub in ["true", "True", "1"]:
                    data["submitted_answers"][answer_name] = pl.to_json(True)
                elif a_sub in ["false", "False", "0"]:
                    data["submitted_answers"][answer_name] = pl.to_json(False)
                else:
                    data["format_errors"][name] = "Invalid format. Not a boolean."
                    data["submitted_answers"][answer_name] = None


def grade(element_html: str, data: pl.QuestionData) -> None:
    """
    Grade the submitted answers.
    
    This function is called to grade the submitted answers.
    
    Args:
        element_html: The HTML of the element.
        data: The data object for the question.
        
    Returns:
        None
    """
    incorrect_message = ""

    element = lxml.html.fragment_fromstring(element_html)
    name = pl.get_string_attrib(element, "answers-name")

    # Check if the question is marked as material (informational)
    is_material = pl.get_boolean_attrib(element, "is-material", False)
    path_only = pl.get_boolean_attrib(element, "path-only", False)
    alignment_type = pl.get_string_attrib(element, "type", ALIGNMENT_TYPE_DEFAULT)

    # If it's material, skip grading
    if is_material:
        return

    w_string = "-" + data["params"].get("w")
    v_string = "-" + data["params"].get("v")
    num_rows = len(v_string)
    num_columns = len(w_string)

    score_sum = 0
    if not path_only:
        for row_index in range(num_rows):
            for col_index in range(num_columns):
                # cheking the value
                answer_name = f"{name}_{row_index}_{col_index}"
                a_tru = pl.from_json(data["correct_answers"].get(answer_name, None))
                if a_tru is None:
                    break
                a_sub = data["submitted_answers"].get(answer_name, None)
                if a_tru != a_sub:
                    if incorrect_message == "":
                        incorrect_message = f"You made a mistake when filling the number ({v_string[row_index]}, {w_string[col_index]}) at row {row_index}, column {col_index} (Indicated by a stripe pattern). Please correct it and check all dependent cells.\n You will not get any feedback on the path before you get all numbers correct."
                else:
                    score_sum += 1

    path_score = 1
    # Check the path input
    highlighted_path = []
    for row_index in range(num_rows):
        for col_index in range(num_columns):
            answer_name = f"{name}_{row_index}_{col_index}_p"
            a_sub = data["submitted_answers"].get(answer_name, None)

            if a_sub is not None and a_sub is True:
                highlighted_path.append([row_index, col_index])
    if len(highlighted_path) == 0:
        if incorrect_message == "":
            incorrect_message = "You have not selected any path. Please select a path."
        path_score = 0
    else:
        # check start index
        i, j = highlighted_path[0]
        if alignment_type == "global":
            # global alignment must start at (0, 0)
            if i != 0 or j != 0:
                if incorrect_message == "":
                    incorrect_message = "You path has wrong ending index. Global alignment must start at (0, 0). Please correct it and check all dependent cells."
                path_score = 0
        elif alignment_type == "fitting":
            # fitting alignment  must start at or (0, j)
            if i != 0:
                if incorrect_message == "":
                    incorrect_message = "You path has wrong ending index. Fitting alignment must start at the first row. Please correct it and check all dependent cells."
                path_score = 0
        a_sub = data["correct_answers"].get(f"{name}_{i}_{j}", None)
        if a_sub is not None and a_sub != 0:
            if incorrect_message == "":
                incorrect_message = "You path has wrong ending index. Please correct it and check all dependent cells."
            path_score = 0
        # check end index
        i, j = highlighted_path[-1]
        if alignment_type == "global":
            # global alignment must end at (len(v), len(w))
            if i != num_rows - 1 or j != num_columns - 1:
                if incorrect_message == "":
                    incorrect_message = "You path has wrong starting index. Global alignment must end at (len(v), len(w)). Please correct it and check all dependent cells."
                path_score = 0
        elif alignment_type == "fitting":
            # fitting alignment  must end at or (i, len(w))
            if i != num_rows - 1:
                if incorrect_message == "":
                    incorrect_message = "You path has wrong starting index. Fitting alignment must end at the last row). Please correct it and check all dependent cells."
                path_score = 0
        a_sub = data["correct_answers"].get(f"{name}_{i}_{j}", None)
        score = data["correct_answers"].get(f"{name}_score", None)
        if a_sub is not None and score is not None and a_sub != score:
            if incorrect_message == "":
                incorrect_message = "You path has wrong starting index. Please correct it and check all dependent cells."
            path_score = 0
        if path_score == 1:
            p_i, p_j, i, j = -1, -1, 0, 0
            while len(highlighted_path) > 0:
                i, j = highlighted_path.pop(-1)
                if p_i >= 0 and p_j >= 0:
                    a_sub = data["correct_answers"].get(f"{name}_{i}_{j}", None)
                    a_sub_p = data["correct_answers"].get(f"{name}_{p_i}_{p_j}", None)
                    if i == p_i - 1 and j == p_j - 1:
                        # move DIAGONAL
                        if not (
                            (
                                v_string[p_i] == w_string[p_j]
                                and a_sub == a_sub_p - PENALTY_SCORE_DEFAULT
                            )
                            or (
                                v_string[p_i] != w_string[p_j]
                                and a_sub == a_sub_p + PENALTY_SCORE_DEFAULT
                            )
                        ):
                            path_score = 0
                    elif i == p_i - 1 and j == p_j:
                        # move TOP
                        if not a_sub == a_sub_p + PENALTY_SCORE_DEFAULT:
                            path_score = 0
                    elif i == p_i and j == p_j - 1:
                        # move LEFT
                        if not a_sub == a_sub_p + PENALTY_SCORE_DEFAULT:
                            path_score = 0
                    else:
                        path_score = 0
                    if path_score == 0:
                        if incorrect_message == "":
                            incorrect_message = f"You path is incorrect at ({v_string[i]}, {w_string[j]}) at row {i}, column {j} (Indicated by a stripe pattern). Please correct it and check all dependent cells."
                        break
                p_i, p_j = i, j
    if path_only:
        data["partial_scores"][name] = {
            "score": path_score,
            "weight": 1,
            "feedback": incorrect_message,
        }
    else:
        data["partial_scores"][name] = {
            "score": 0.5 * score_sum / (num_rows * num_columns) + 0.5 * path_score,
            "weight": 1,
            "feedback": incorrect_message,
        }


def test(element_html: str, data: pl.ElementTestData) -> None:
    return
