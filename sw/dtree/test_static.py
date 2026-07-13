# test_static.py
# 8 May 2026     JMA
"""Read a decision table from a file, and display its webpage."""

import pandas as pd
from decision_table import DecisionTable
from static_display import TableDisplay


new_dt = DecisionTable()
new_dt.load_from_csv()
display = TableDisplay(new_dt)
display.layout_new_table()
display.show()