import pandas as pd
from xml.sax import ContentHandler, parse

# Reference https://goo.gl/KaOBG3
class ExcelHandler(ContentHandler):
    def __init__(self):
        self.chars = [  ]
        self.cells = [  ]
        self.rows = [  ]
        self.tables = [  ]
    def characters(self, content):
        self.chars.append(content)
    def startElement(self, name, atts):
        if name=="Cell":
            self.chars = [  ]
        elif name=="Row":
            self.cells=[  ]
        elif name=="Table":
            self.rows = [  ]
    def endElement(self, name):
        if name=="Cell":
            self.cells.append(''.join(self.chars))
        elif name=="Row":
            self.rows.append(self.cells)
        elif name=="Table":
            self.tables.append(self.rows)

excelHandler = ExcelHandler()
parse(r'C:\Users\ollie\Documents\Python Projects\Charter\McK_colour_exports_v2\uploads\Starbucks_satisfactory_survey_xml.xlsx', excelHandler)
df1 = pd.DataFrame(excelHandler.tables[0][4:], columns=excelHandler.tables[0][3])