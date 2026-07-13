# decision_table.py
# JMA 20 Feb 2026
#
# An API to create and solve Decision Tables

import os, sys
from typing import Optional
import numpy as np
import pandas as pd
from io import StringIO
from colorama import init, Fore, Back, Style

# defaults
STATES = ['absent', 'present']
OPTIONS = ['do_nothing']

class DecisionTable (object):
    
    def __init__(self, tbl_name = 'Decision Table', instant_update=True):
        init()   # should only be called once
        self.tool_errors = {"warning": None, "error": None}
        self.tbl_name = tbl_name
        self.value_matrix = pd.DataFrame()
        self.outcome_probs = pd.Series()
        self.expected_utilities = pd.Series()
        self.maximum_expected_utility = np.nan
        self.best_alternative = 0
        self.instant_update = instant_update       # Recompute expected utilities and max EU
                                                   # whenever the value matrix changes.
    
    def set_default_table(self,
                          outcomes= STATES,
                          outcome_probs = None,
                          values = None): 
        """Set a default decision table.
            Initially assume only one alternative:
        - the default, "do_nothing".
            The default is assumed to have zero value. 

        Parameters
        ----------
            outcomes:
        Column labels representing the possible outcomes (states of nature).
            outcome_probs: optional,  1-D array-like
        Assign probabilities over states of nature.
            values : optional, 1-D array-like 
        """
        state_cnt = len(outcomes)
        if outcome_probs is None:
            # Set uniform outcome probabilities 
            outcome_probs = pd.Series(np.ones(state_cnt)/state_cnt, index=outcomes)
        elif state_cnt != len(np.atleast_1d(outcome_probs).flatten()):
            print(f"ERROR: outcome_probs have length {len(np.atleast_1d(outcome_probs))} and must equal state_cnt which is {state_cnt}.")
            return
        else:
            outcome_probs = pd.Series(np.atleast_1d(outcome_probs), index=outcomes)
        self.outcome_probs = outcome_probs
        if values is None:
            values = np.zeros((1, state_cnt)) # Needs to be a row vector 
        self.value_matrix = pd.DataFrame(
            values,
            index=OPTIONS,
            columns=list(outcomes),
        )
        
    def get_outcome_probs(self) -> pd.Series:
        '''Access function for the outcome probability vector, indexed by column names.'''
        return pd.Series(self.outcome_probs.values, index=self.value_matrix.columns)
    
    def normalize_outcome_probs(self):
        '''Normalize the outcome probabilities to sum to 1.
        
        Returns
        -------
            pd.Series
        The normalized outcome probabilities.
        '''
        total = self.outcome_probs.sum()
        # TODO  How to return the error string explanations to the LLM
        if np.isclose(total, 0.0):
            print("WARNING: total probability is zero. Leaving probabilities unchanged.", file=sys.stderr)
        elif not np.isclose(total, 1.0):
            print("WARNING: renormalizing outcome probabilities to sum to 1.", file=sys.stderr)
            self.outcome_probs = self.outcome_probs / total
        return self.outcome_probs

    def reset_outcome_probs(self, outcome_probs, outcomes=None):
        '''Replace the probability vector, and normalize if necessary.
        
        Parameters
        ----------
            outcome_probs : 1-D array-like
        New probability values.
            outcomes : list, optional
        New column labels for the states of nature. If provided, renames value_matrix columns also
        
        Returns
        -------
            pd.Series
        The updated outcome probabilities.
        '''
        # Check that args values match the len of the current decn table states. 
        prob_array = np.array(outcome_probs, dtype=float)
        # Rename columns if new outcomes labels are provided
        if outcomes is not None:
            self.value_matrix.columns = list(outcomes)
        # Check for zero probability total before updating
        # TODO - if requested outcomes don't match the number of probabilities, 
        # we should return an error instead of trying to update with mismatched dimensions.   
        total = pd.Series(outcome_probs, index=self.value_matrix.columns).sum()
        if np.isclose(total, 0.0):
            self.tool_errors["error"] = "total probability is zero. Leaving probabilities unchanged."
        else:
            # Update the outcome probabilities with the new values, 
            prob_array = np.array(outcome_probs, dtype=float)
            self.outcome_probs = pd.Series(prob_array, index=self.value_matrix.columns)
            # and normalize if necessary
            self.normalize_outcome_probs()
        return self.outcome_probs
        
    ### state
    def add_state(self, the_state_name: str, borrow_prob_weight: Optional[bool] = True):
        '''Default is to decrease existing probabilities to retain normalization
        by borrowing probability weight from existing probabilities.'''
        # Add a new column of zeros to the value matrix
        self.value_matrix[the_state_name] = 0.0
        n = len(self.value_matrix.columns)
        if borrow_prob_weight:
            # Distribute new state's probability weight uniformly from existing states
            new_prob = 1.0 / n
            existing_probs = self.outcome_probs.values * (1.0 - new_prob)
            new_probabilities = np.append(existing_probs, new_prob)
        else:
            # Just add with zero probability and renormalize
            new_probabilities = np.append(self.outcome_probs.values, 0.0)
        self.outcome_probs = pd.Series(new_probabilities, index=self.value_matrix.columns)
        self.reset_outcome_probs(self.outcome_probs.values)
        if self.instant_update:
            self.table_update()
    
    def remove_state(self, the_state_name: str):
        '''Delete the column from the value matrix for this state, 
        checking if remaining state probabilities remain positive.
        
        Parameters
        ----------
            the_state_name : str
        Name of the state to remove. Must be a column label in the value matrix.    
        '''
        provisional_matrix = self.value_matrix.copy().drop(columns=[the_state_name])
        provisional_probs = self.outcome_probs.drop(labels=[the_state_name]).values
        total = provisional_probs.sum()
        # THere is a corner case if the removed state had all the probability mass.
        if np.isclose(total, 0.0):
            self.tool_errors["error"] = "ERROR: You are left without any states with probability mass.\nReverting to original states"
            return 
        else:
            # Remember to renormalize probabilities
            self.value_matrix = provisional_matrix
            # self.outcome_probs = pd.Series(provisional_probs, index=self.value_matrix.columns)
            # Renormalize remaining probabilities to sum to 1 
            self.reset_outcome_probs(provisional_probs, outcomes=self.value_matrix.columns)
            if self.instant_update:
                self.table_update()
    
    ### alternative
    def add_alternative(self, the_alternative_name: str, alternative_values: np.array):
        '''Append the row to the value matrix for this alternative, adding the alternative to its index.'''
        # extended_options = self.value_matrix.index.append(pd.Index([the_alternative_name]))
        new_row = pd.DataFrame(
            [np.atleast_1d(alternative_values)],
            index=pd.Index([the_alternative_name]),
            columns=self.value_matrix.columns
        )
        self.value_matrix = pd.concat([self.value_matrix, new_row])
        if self.instant_update:
            self.table_update()
    
    def remove_alternative(self, the_alternative_name: str):
        '''Delete the row from the value matrix for this alternative.'''
        self.value_matrix = self.value_matrix.drop(index=[the_alternative_name])
        if self.instant_update:
            self.table_update()
        
    def get_alternative(self, the_alternative_name: str) -> pd.Series:
        'Accessor function to return a copy of a designated row of the value matrix'
        return pd.Series(self.value_matrix.loc[the_alternative_name], index=self.value_matrix.columns)
    
    ### value
    def reset_value(self, the_alternative_name: str, the_state_name: str,new_value):
        '''Update the corresponding cell in the value matrix. '''
        self.value_matrix.loc[the_alternative_name, the_state_name] = new_value
        if self.instant_update:
            self.table_update()
    
    def get_value(self, the_alternative_name: str, the_state_name: str) -> float:
        '''Access function for a value matrix cell'''
        return self.value_matrix.loc[the_alternative_name, the_state_name]

    ### solve
    def take_expectation(self):
        'Take expectation to reduce the rows'
        self.expected_utilities = self.value_matrix @ self.outcome_probs
        
    def max_expected_utility(self):
        'Maximize over the expected utilities to find the best alternative.'
        # Maximize over the rows
        self.maximum_expected_utility = self.expected_utilities.max()
        self.best_alternative = self.expected_utilities.idxmax()
        
    def table_update(self):
        'Keep the MEU consistent when the table changes'
        self.take_expectation()
        self.max_expected_utility()
        
    ### CSV file input and output. 
    def save_to_csv(self, filename='decision_table.csv'):
        '''Save the value matrix and probabilities to a CSV file.
        
        csv format:
        title row,
        value matrix dataframe with header,
        Probabilities row with the same columns as the value matrix, and a blank cell for the expected utility column,
        '''
        # Add the probabilties as the first row 
        output_df = self.value_matrix.copy()
        output_df.loc['Probabilities'] = self.outcome_probs.values
        # Add the expected utilities as the last column, leavint the probabilities row blank in that column
        output_df['Expected Utility'] = np.insert(self.expected_utilities.values, len(self.expected_utilities.values), np.nan)
        # Prepend a row with the title, then append the value matrix as CSV
        value_string = StringIO()
        value_string.write(f'"{self.tbl_name}"\n')
        value_string.write(output_df.to_csv(header=True))
        with open(filename, 'w') as f:
            f.write(value_string.getvalue())
            
    def load_from_csv(self, filename='decision_table.csv'):
        '''Load the value matrix and probabilities from a CSV file, assuming the format described in save_to_csv.'''
        # Read the title line once, then parse the remainder of the CSV into a DataFrame.
        with open(filename, 'r') as f:
            title_line = f.readline().strip()
            csv_body = f.read()
        self.tbl_name = title_line.strip().replace('"', '').replace(',', '')  # Remove quotes and commas if present
        df = pd.read_csv(StringIO(csv_body), index_col=0)
        # Extract the probabilities from the "Probabilities" row.
        self.outcome_probs = df.loc['Probabilities'].drop(labels='Expected Utility', errors='ignore')
        # Remove the "Probabilities" row and "Expected Utility" column from the value matrix.
        self.value_matrix = df.drop(index='Probabilities').drop(columns=['Expected Utility'], errors='ignore')
        # Update expected utilities and maximum expected utility
        self.normalize_outcome_probs() 
        self.table_update()
            
    ### visualize
    def pr_probs(self):
        'the outcome probs.'
        row_probs = pd.DataFrame([np.atleast_1d(self.outcome_probs)],
            index=pd.Index(['Probabilities']),
            columns=self.value_matrix.columns)
        print(Fore.CYAN + f'\n{row_probs}')
        print(Style.RESET_ALL)
        
    def pr_decision_table(self):
        'Visualize for the user'
        print(f'\n\tvalue matrix\n{self.value_matrix}')
        
    def pr_all(self):
        'The full model'
        # Add a divider column
        self.pr_errors()
        self.table_update()
        pr_temp = self.value_matrix.copy()
        div = pd.Series('|', dtype='str', index = pr_temp.index)
        # Add a divider column to the right of the value matrix, and the EV column to the right of that    
        pr_temp['-'] = div
        pr_temp['EV'] = self.expected_utilities
        # Add the probabilities as a row above
        row_probs = pd.DataFrame(columns=pr_temp.columns)
        row_probs.loc['Probabilities'] =  list(self.outcome_probs) +['|', ' ']
        row_probs.loc['-'] =  len(row_probs.columns) * ['_']
        display_table = pd.concat([row_probs, pr_temp])
        table_string = display_table.to_string(float_format=lambda value: f"{value:0.2f}")
        if self.best_alternative in display_table.index:
            lines = table_string.splitlines()
            best_label = str(self.best_alternative)
            for index, line in enumerate(lines):
                tokens = line.strip().split()
                if tokens and tokens[0] == best_label:
                    lines[index] = f"{Fore.GREEN}{line}{Style.RESET_ALL}"
                    break
            table_string = "\n".join(lines)
        print(f'\t{self.tbl_name}\n{table_string}')
        print(Style.RESET_ALL)
        
    def pr_errors(self ):
        'Print any warnings or errors from the last tool use.'
        if self.tool_errors["warning"] is not None:
            print(f"{Fore.YELLOW}WARNING: {self.tool_errors['warning']}{Style.RESET_ALL}")
        if self.tool_errors["error"] is not None:
            print(f"{Fore.RED}ERROR: {self.tool_errors['error']}{Style.RESET_ALL}")
        self.tool_errors = {"warning": None, "error": None}  # Clear errors after printing  
   
    # TODO Add conversion to Genie formats
        
### MAIN ###############################################################################        
if __name__ == '__main__':
# Show a Decision Table as a DataFrame
# and solve for the Maximum Expected Utility

    a_dt = DecisionTable('Investments Decision')
    # a_dt.set_default_table(outcome_probs= np.ones((1,1)))
    a_dt.set_default_table()
    a_dt.pr_decision_table()
    
    # A vector of outcome probabilities TODO do we need a constructor? 
    outcome_probs = [0.8, 0.2]
    a_dt.pr_probs()

    # Show a Decision Table as a DataFrame
    # and solve for the Maximum Expected Utility
    # Update the decision table with the new states and probabilities
    a_dt.reset_outcome_probs(outcome_probs, outcomes=['clear', 'cloudy'])
    a_dt.take_expectation()
    print(f'\n\texpected_utilities\n{a_dt.expected_utilities}')
    
    a_dt.max_expected_utility()
    print(f'\n\tmaximum_expected_utility\n{a_dt.maximum_expected_utility}')

    a_dt.reset_value('do_nothing', 'clear', 99)
    a_value = a_dt.get_value('do_nothing', 'clear')
    print(f'a_value =  {a_value}\n')
    a_dt.take_expectation()
    a_dt.pr_all()
    # print(f'\n\texpected_utilities\n{a_dt.expected_utilities}')
    
    # a_dt.max_expected_utility()
    # print(f'\n\tmaximum_expected_utility\n{a_dt.maximum_expected_utility}')
    
    # state and alternative, and set automated update. 
    a_dt.instant_update = True
    a_dt.add_alternative('invest', [1.0, 5.0])
    a_dt.pr_all()
    
    probs = a_dt.get_outcome_probs()
    probs['clear'] = 0.0
    a_dt.reset_outcome_probs(probs)

    a_dt.add_state('rain', True)
    print(f'\tdo_nothing:\n {a_dt.get_alternative('do_nothing')}\n')
    a_dt.pr_all()
    a_dt.save_to_csv()
    new_dt = DecisionTable()
    new_dt.load_from_csv()
    new_dt.pr_all()
    
    a_dt.remove_state('cloudy')
    a_dt.pr_all()
    