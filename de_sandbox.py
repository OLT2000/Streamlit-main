from pathlib import Path
import openpyxl
import regex 
from typing import List
import json


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
            current_table.append([*row])

    if current_table:
        tables.append(current_table)

    return tables



filepath = Path.cwd() / "survey_pk" / "Database and questions.xlsx"

# Compile a RegEx pattern to identify screening question.
#   (?<=^\[|^)? ensures that the match starts with either "[" or "", but does not match this part.
#   S\d+ quite literally matches S, followed by 1 or more digits
#   (?=[^\]:]*[\]:]) ensures the "S\d+" is followed by any character that isn't "]" or ":", and ends with an optional "]" followed by a necessary ":"

# re_tests = """[S1r4oe]: Which geography do you cover? - Other (please specify)
# [Q0]: Please choose your language preference:
# [HidSamp]: Hidden to punch sample
# [S1]: Which geography do you cover?
# S1_term: S0 TERMINATE
# [noooo S1]
# S1 Please NO""".split("\n")

# for st in re_tests:
#     print(st, regex.search(question_regex, st))
#     # print(st, regex.search(r'(?<=^\[?)S\d+(?=[^\]:]*\]?:)', st))


question_regex = regex.compile(r'(?<=^\[?)(S|Q)\d+(?=[^\]:]*\]?:)')
all_field_regex = regex.compile(r'(?<=^)\[?[\w^\]^:]+\]?:')


wb = load_workbook(filepath=filepath)
sheet = load_worksheet(workbook=wb, sheet_name="Datamap")


def clean_row(row):
    cleaned_row = []
    for cell in row:
        if cell.value == "":
            cell.value = None


# metadata = dict()
# screening_questions = dict()
# survey_questions = dict()
all_keys = dict()


prev_row = (None)
for row in sheet.iter_rows():
    clean_row(row)
    if not all(c.value is None for c in row):
        # Check that previous row was empty
        first_cell, *_ = row
        assert first_cell.column == 1

        if first_cell.row > 1:
            # prev_row = sheet.iter_rows(min_row=first_val.row, max_row=first_val.row)
            # clean_row(prev_row)
            if all(c.value is None for c in prev_row):
                # Check to see if we have a question/screening field
                field_code = regex.search(all_field_regex, first_cell.value)
                if not field_code:
                    print(f"Could not identify a field code for the cell {first_cell.value} ({first_cell.row}, {first_cell.column})")
                    continue

                else:
                    field_code = field_code.group(0)
                
                is_column = regex.search(r"^\[\w+\]:$", field_code) is not None
                

                field_search = regex.search(question_regex, field_code)
                if field_search:
                    key = field_search.group(0)
                    is_metadata = False

                else:
                    is_metadata = True
                    if is_column:
                        key = field_code[1:-2]
                    else:
                        key = field_code
                
                if key in all_keys.keys():
                    print(f"Found a duplicate key {key} for {first_cell.value}")

                else:
                    primary_text = regex.search(r'(?<=^\[?\w+\]?: ).+', first_cell.value)
                    if not primary_text:
                        print(f"No primary text found for {field_code}")
                    
                    else:
                        primary_text = primary_text.group(0)

                    all_keys[key] = {
                        "is_column": is_column,
                        "is_metadata": is_metadata,
                        "primary_text": primary_text,
                        "schema_row_start": first_cell.row,
                    }

                # if not regex_search:
                #     # This is a non-screener or survey question I.E. Metadata
                #     if first_cell.value in all_keys.keys():
                #         print(f"Found a duplicate metadata key at row {first_cell.row}: {first_cell.value}")

                #     else:
                #         key = regex.search(all_field_regex, first_cell.value).group(0)
                #         all_keys[regex.search(all_field_regex, first_cell.value).group(0)] = {
                #             "schema_row_start": first_cell.row
                #         }

                # else:
                #     # print(first_cell.value, regex_search)
                #     primary_key = regex_search.group(0)
                #     if primary_key in all_keys.keys():
                #         print(f"Found a duplicate survey/screening key at row {first_cell.row}: {primary_key} + {first_cell.value}")

                #     else:
                #         all_keys[primary_key] = {
                #             "schema_row_start": first_cell.row
                #         }

    prev_row = row

# Sort the dictionary items based on 'schema_row_start' and iterate through them
sorted_keys = sorted(all_keys, key=lambda x: all_keys[x]["schema_row_start"])

# Loop through the sorted keys to set 'schema_row_end' for each
for i in range(len(sorted_keys) - 1):
    current_key = sorted_keys[i]
    next_key = sorted_keys[i + 1]
    # Set 'schema_row_end' to be one less than the 'schema_row_start' of the next item
    all_keys[current_key]['schema_row_end'] = all_keys[next_key]["schema_row_start"] - 1

# Add max row at the bottom
last_key = sorted_keys[-1]
all_keys[last_key]["schema_row_end"] = sheet.max_row



# def is_row_a_field_gen(row_gen):
    # if 


for primary_key, table_data in all_keys.items():
    row_start = table_data["schema_row_start"]
    row_end = table_data["schema_row_end"]
    is_col = table_data["is_column"]
    field_type = sheet.cell(row=row_start+1, column=1).value
    sub_dict = dict()
    prev_row = (None)
    if is_col:
        map_range = regex.search(r"(?<=Values: ?)\d+-\d+$", field_type)
        if map_range:
            value_map_start = map_range.group(0).split("-")[0]
            value_map_end = map_range.group(0).split("-")[1]
            
            if str.isnumeric(value_map_start) and str.isnumeric(value_map_end):
                encoding_table = [
                    [c.value for c in r]
                    for r in sheet.iter_rows(min_col=2, max_col=3, min_row=row_start+2, max_row=row_start+1+(int(value_map_end) - int(value_map_start) + 1))
                ]
                all_keys[primary_key]["encodings"] = dict(encoding_table)

            else:
                print(f"Found Non-Numeric Value Map {map_range} for {primary_key}")

            all_keys[primary_key]["column_type"] = "single_select"

        else:
            print(f"Found No Value Map of {field_type} for {primary_key}")
            all_keys[primary_key]["column_type"] = field_type

        all_keys[primary_key]["related_cols"] = [primary_key]
        

print(json.dumps(all_keys, indent=4))

    # for row in :
    #     if not all(c.value is None for c in row):
    #         field_code = regex.search(all_field_regex, first_cell.value)
    #         if not field_code:
    #             print(f"Could not identify a field code for the cell {first_cell.value} ({first_cell.row}, {first_cell.column})")
    #             continue

    #         else:
    #             field_code = field_code.group(0)
            
    #         is_column = regex.search(r"^\[\w+\]:$", field_code) is not None

    #     else:
    #         pass