# table_display.py
# 28 April 2026     JMA
"""Display decision table in a browser window.
"""

import streamlit as st
import decision_table

class TableDisplay (object):
    """Display a decision table in a browser window.
    """
    def __init__ (self, decn_table):
        self.table = decn_table.value_matrix
        self.title = decn_table.tbl_name
        

    def show (self):
        """Show the decision table in a browser window.
        """
        st.title("Decision Table")
        # st.table(self.table)
        # st.data_editor(self.table, num_rows="dynamic")
        st.write(self.table)
    
    
if __name__ == "__main__":
    table = decision_table.DecisionTable()
    table.set_default_table()
    display = TableDisplay(table)
    display.show()
    print("Done!")