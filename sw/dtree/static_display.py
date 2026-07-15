# static_display.py
# 8 May 2026     JMA
"""Display a static decision table in a browser window.
"""

#import webbrowser as wb
import sys 
import pandas as pd
from matplotlib import style
# import polars as pl
from great_tables import GT, md, html, loc, style, system_fonts

import decision_table
DT_CSV = "decision_table.csv"
SIG_DIGITS = 2

class TableDisplay (object):
    """Display a decision table in a browser window.
    """
    def __init__ (self, decn_table, table_title="Decision Table"):
        'Copy the decision table into the display object.'
        self.table = decn_table.value_matrix.copy()
        # Add the probabiligies as a row at the bottom of the table.
        decn_table.outcome_probs.name = "" # Hack to remove the name of the series, so it doesn't show up as a row label in the table.
        outcome_probs = decn_table.outcome_probs.to_frame().T.reindex(columns=self.table.columns, fill_value=pd.NA)
        self.table = pd.concat([self.table, outcome_probs], axis=0)
        # Then add a column for the expected utilities. 
        self.expected_utilities = decn_table.expected_utilities
        self.table['Expected utilities'] = self.expected_utilities
        # Grab the row labels, and make them a column in the dataframe.
        self.table.insert(0, "Alternatives", self.table.index)
        self.table.reset_index(inplace=True, drop=True)
        # Create a new column to group the probabilities and alternatives, so we can style them differently.
        self.table = self.table.assign(group= ['Alternatives'] * (len(self.table.index) - 1) + ['Probabilities'])
        # Copy utility information  
        self.maximum_expected_utility = decn_table.max_expected_utility
        self.best_alternative = decn_table.best_alternative
        self.title = decn_table.tbl_name
        self.table_title = table_title
        
    def layout_new_table (self):
        '''A new undecorated table'''
        self.formatted_table = GT(self.table, rowname_col="Alternatives", groupname_col="group")\
            .tab_header(title=self.table_title, subtitle=self.title)\
            .tab_options(table_font_names=system_fonts("handwritten"), row_group_font_weight=2000) #, row_group_padding=0, column_group_padding=0, row_group_border_width=0, column_group_border_width=0, row_group_border_color="white", column_group_border_color="white")\
        self.formatted_table = self.formatted_table.tab_stubhead(label="") 

    def show (self):
        """Show the decision table in a browser window.
        """
        cols = self.table.columns.tolist()
        rows = self.table.index.tolist()
        # Note that the columns in the span must exist in the dataframe. 
        # Note the group column is not presented, but it remains the last column in the Gtable object 
        # and must be excluded from formatting and the utilities span.
        # bold the probabilities row and color the best alternative row light green.
        self.formatted_table = self.formatted_table\
            .tab_spanner(label=md("**Utilities**"), columns= cols[1:-2], )\
            .tab_style(style.fill(color="lightgreen"), locations=loc.body(rows=self.best_alternative))\
            .tab_style(style=style.text(weight="italic"), locations= loc.body(rows=[-1]))\
            .fmt_number(columns=cols[1:-1], decimals=SIG_DIGITS)
            # polars fails to load via pip install, so we can't use the .fmt_nanoplot method.
            # .fmt_nanoplot(columns='expected_utility', plot_type="bar")
        GT.show(self.formatted_table)
    
#### MAIN ###############################################################################
if __name__ == "__main__":

    if len(sys.argv) > 1 and isinstance(sys.argv[1], type('str')):
        DT_CSV = sys.argv[1]
    
    table = decision_table.DecisionTable() # The name is taken from the csv file  
    table.load_from_csv(DT_CSV)  # t be_from_csv method of the DecisionTable class.
    display = TableDisplay(table) # The table title can be set here. 
    display.layout_new_table()
    display.show()
    print("Done!")