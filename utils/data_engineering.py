
import openpyxl
import json
from pathlib import Path
from typing import List
import openpyxl.workbook
import re


def load_workbook(filepath: Path) -> openpyxl.workbook.workbook.Workbook:
    # if filepath.suffix != ".xlsx":
    #     raise ValueError(
    #         f"The inputted file is of type {filepath.suffix}. Please provide a .xlsx file."
    #     )

    try:
        workbook = openpyxl.load_workbook(filepath)

    except Exception as e:
        raise f"An unexpected error occurred: {e}"

    else:
        return workbook


def load_worksheet(
    workbook: openpyxl.workbook.workbook.Workbook, sheet_name: str
) -> openpyxl.worksheet.worksheet.Worksheet:
    if sheet_name not in workbook.sheetnames:
        raise KeyError(f"Sheet '{sheet_name}' cannot be found in workbook.")

    else:
        return workbook[sheet_name]


def parse_sheet_data(worksheet: openpyxl.worksheet.worksheet.Worksheet) -> List[List]:
    tables = []
    current_table = []
    for row in worksheet.iter_rows(values_only=True):
        if all(cell is None for cell in row):
            if current_table:
                tables.append(current_table)
                current_table = []

        else:
            current_table.append([r for r in row if r is not None])

    if current_table:
        tables.append(current_table)

    return tables


def parse_table_data(table: List[List]) -> dict:
    if len(table) < 2:
        return None

    column_name, column_description = table.pop(0)
    column_type = table.pop(0)[1]
    encodings = {key: value for key, value in table if key is not None}

    return {
        "column_name": column_name,
        "column_description": column_description,
        "column_type": column_type,
        "encodings": encodings,
    }


# def process_all_tables(processed_tables: list[dict]):
#     current_key = None

#     for table in processed_tables:



def load_question_schema(filepath: Path, sheet_name: str) -> List[dict]:
    wb = load_workbook(filepath=filepath)
    sheet = load_worksheet(workbook=wb, sheet_name=sheet_name)
    processed_tables = parse_sheet_data(sheet)
    row_match_pattern = re.compile(r".*(R\d+){1}(_97_OTH|_97_OTH_english_uk)?$")
    row_look_behind = re.compile(r"^(.*)(?=((R\d+)(_97_OTH|_97_OTH_english_uk)?)$)")
    other_match_pattern = re.compile(r".*(_97_OTH|_97_OTH_english_uk)$")


    result_dict = dict()

    for table in processed_tables:
        field_code, field_text = table.pop(0)
        response_type = table.pop(0)[1]
        encodings = {key: value for key, value in table if key is not None}

        # Remove non-Q fields:
        if not field_code.startswith("Q"):
            # print(f"Non Q-field {field_code}")
            result_dict[field_code] = {
                "field_text": field_text,
                "response_type": response_type,
                "encodings": encodings,
                "question_type": "single"
            }

        # Market Quotas
        elif field_code.startswith("QMKT"):
            # print(f"Quota Field {field_code}")
            result_dict[field_code] = {
                "field_text": field_text,
                "response_type": response_type,
                "encodings": encodings,
                "question_type": "quotas"
            }
            # I think this will require some quite complex DE as it seems to use rules and other columns.
            # For example, "QUOTA \| by country - current user of target brand (SFUNN = 6)"
            #               Is a quota of the previous data QTARGET, grouped by country.
            # primary_key = field_code[4:]

        else:
            field_code = field_code[1:]
            # Identify tabular questions
            if re.match(row_match_pattern, field_code):
                # print(f"Identified row: {field_code}. Field Text: {field_text}")
                primary_key = re.search(row_look_behind, field_code).group(0)
                # print(other_match_pattern, re.match(other_match_pattern, field_code))
                if re.match(other_match_pattern, field_code):
                    primary_text = field_text
                    secondary_text = ""
                else:
                    primary_text, secondary_text = field_text.split(" | ", 1)

                # print(field_code)
                row_number = re.search(
                    # r"(?<=R)\d+$",
                    r"(?<=R)\d+(|_97_OTH|_97_OTH_english_uk)$",
                    re.search(row_match_pattern, field_code).group(0)
                ).group(0)

                secondary_dict = {
                                "sub_field": secondary_text,
                                "row_number": row_number,
                                "column": field_code
                            }
                
                if primary_key not in result_dict:
                    result_dict[primary_key] = {
                        "field_text": primary_text,
                        "response_type": response_type,
                        "encodings": encodings,
                        "question_type": "table",
                        "rows": [
                            secondary_dict
                        ]
                    }

                else:
                    # Check everything matches
                    key_data = result_dict[primary_key]
                    if not re.match(
                        other_match_pattern,
                        field_code
                    ):
                        assert primary_text == key_data["field_text"], f"Current field {field_code} does not match the results found:\n\t{key_data}."

                        assert response_type == key_data["response_type"], f"Current field {field_code} does not match the results found:\n\t{key_data}."

                        assert row_number not in [r["row_number"] for r in key_data["rows"]], f"Found duplicate row numbers {row_number} for field code {field_code}."

                        assert field_code not in [r["column"] for r in key_data["rows"]], f"Found duplicate field codes {field_code}."

                        for code, val in encodings.items():
                            assert val == key_data["encodings"][code], f"Encodings do not match for field code {field_code}."

                        key_data["rows"].append(
                            secondary_dict
                        )
            
            else:
                # print(f"Other field: {field_code}")
                result_dict[field_code] = {
                "field_text": field_text,
                "response_type": response_type,
                "encodings": encodings,
                "question_type": "single"
            }


    return result_dict
    # return [parse_table_data(t) for t in processed_tables]


if __name__ == "__main__":
    import pandas as pd
    file_path = Path(__file__).parent.parent / "survey.xlsx"
    json_output = load_question_schema(filepath=file_path, sheet_name="Questions")
    survey_fields = dict()
    other_fields = dict()
    # for metadata in json_output:
    #     col_name = metadata.pop("column_name")
    #     if col_name.startswith("Q"):
    #         survey_fields[col_name] = metadata
    #     else:
    #         other_fields[col_name] = metadata
    # question_df = pd.DataFrame.from_records(json_output).drop(columns=["encodings"])

    # def str_helper(row):
    #     if row["column_type"] == "checkbox" and "_" in row["column_name"]:
    #         output = row["column_name"].split("_", 1)
        
    #     else:
    #         output = [row["column_name"], ""]
        
    #     return output
        
    # question_df[["qcode", "subq"]] = question_df.apply(lambda r: str_helper(r), axis=1, result_type="expand")
    # with pd.option_context({"display.max_columns": None}):
    #     print(question_df.head(20))
    # print(json.dumps())
    # with open("question_schema.json", "w") as f:
    #     json.dump(json_output, f, indent=4)


    # data = pd.read_excel(file_path, sheet_name="Data", header=0)
    # with open("../survey_data.csv", "w") as f:
    #     data.to_csv(f, header=True, index=False)
