class Variable:
    def __init__(self, variable_id: str, variable_metadata: dict) -> None:
        self.variable_id = variable_id
        self.question_text = variable_metadata["question_text"]
        self.columns = variable_metadata["related_columns"]
        self.is_column = variable_metadata["is_column"]
        self.encodings = variable_metadata.get("encodings")
        self.rows = variable_metadata.get("rows")