#!/usr/bin/env python
# coding: utf-8
#     JMA 3 Aug 2026

'''
 # Tornado Diagram Plot Create a plot of a tornado diagram as used in decision analysis. 
 A tornado diagram is a horizontal bar plot showing the sensitivity of the utility function 
 to each input variable, separately. Each variable is shown by a bar.  The  bar plots the utility 
 function for the 10th percentile and 90th percentile of the variable, with all other variables set 
 to their median value -- their 50th percentile.  The bars are centered at their 50th percentile utility. 
 
 The input to the diagram is a pandas dataframe, vars,  with variables naming the rows. 
 Probability variables have their P10, P50 and P90 values in columns.  
 The utility function is a python function named utility() whose arguments include all variables, 
 and which returns a numeric value. 
 
 The output is the table of utility ranges for the P10 and P90 values of each variable, 
 sorted by largest range to smallest range.  This output is plotted as a horizontal bar chart.

 Args:
    -t:          Run test
    <file>.csv:  Use csv file for P10-P90 ranges
'''

import os, sys
import numpy as np
import pandas as pd

from bokeh.io import output_file, show
from bokeh.models import ColumnDataSource, Label, Span
from bokeh.plotting import figure


def test(html_file):

    assert len([test_utility(100, 99, 0.2, 5, 20000,k,  5000) for k in np.linspace(0, 20000, 10)]) == 10

    intervals = [
        {'var':'price', 'P10':10 ,  'P50':100 , 'P90':200 },
        {'var':'quantity', 'P10':99 ,  'P50':199 , 'P90':299 },
        {'var':'discount' ,'P10':0.0 ,  'P50':0.03 , 'P90':0.12 },
        {'var':'years' ,'P10':4 ,  'P50':10 , 'P90':20 },
        {'var':'initial' ,'P10':5000 ,  'P50':10000 , 'P90':25000 },
        {'var':'final' ,'P10':10000 ,  'P50':20000 , 'P90':60000 },
        {'var':'fixed' ,'P10':3000 ,  'P50':5000 , 'P90':8000 },
    ]
    vars = pd.DataFrame(intervals).set_index('var')

    tornado_table = build_utility_table(vars, test_utility)
    tornado_figure = plot_tornado(tornado_table)
    output_file(filename=html_file)
    show(tornado_figure)


def test_utility(price, quantity, discount, years, initial, final, fixed):
    'The value of one instance of the variables relevant to the utility.'

    # Only integers can be iterated over.  Since python doesn't type check. 
    years = int(years)

    annual = price*quantity - fixed
    yrs = np.ones(years) * annual
    yrs[0] = yrs[0] - initial
    yrs[years-1] = yrs[years-1] + final
    rate = np.ones(years) * (1-discount)
    rates = np.cumprod(rate)
    cash_flow = np.multiply(yrs, rates)
    return float(cash_flow.sum())


def build_utility_table(vars_df, utility):
    """Return a DataFrame of utility swings per variable.

    For each row in vars_df (index = variable name; columns P10,
    P50, P90), evaluate utility at three points with every other
    variable held at P50. Sort by absolute range, largest first.
    """
    ## Build the utility-range table
    # 
    # For each row in `vars`, evaluate `utility` at three points while holding every other variable 
    # at its P50 (median):
    # 
    # * `U_P10`  = utility at the row's P10, all others at P50
    # * `U_base`= utility at the row's P50, all others at P50  (same for every row)
    # * `U_P90`  = utility at the row's P90, all others at P50
    # 
    # The bar for the variable spans from `U_P10` to `U_P90` and is centered on `U_base`. 
    # The table is sorted by absolute range (|U_P90 - U_P10|) so the most influential variables 
    # appear at the top of the chart.

    # The table variables must match the argument list for the utility function
    var_names = list(vars_df.index)
    base = {name: vars_df.loc[name, 'P50'] for name in var_names}
    u_base = utility(**base)

    rows = []
    for name in var_names:
        # copy the dict
        p10 = dict(base); 
        # Set the p10 value for that variable 
        p10[name] = vars_df.loc[name, 'P10']
        # Set the p90 value
        p90 = dict(base); 
        p90[name] = vars_df.loc[name, 'P90']
        u_p10 = utility(**p10)
        u_p90 = utility(**p90)
        swing = u_p90 - u_p10
        rows.append({
            'Variable': name,
            'P10': float(vars_df.loc[name, 'P10']),
            'P50': float(vars_df.loc[name, 'P50']),
            'P90': float(vars_df.loc[name, 'P90']),
            'U_P10': u_p10,
            'U_base': u_base,
            'U_P90': u_p90,
            'Range': swing,
            'Range_abs': abs(swing),
        })
    table = pd.DataFrame(rows)
    return table.sort_values('Range_abs', ascending=False).reset_index(drop=True)


def plot_tornado(table):

    # Largest swing on top, so reverse the y-range.
    y_vars = list(table['Variable'])[::-1]
    u_p10 = [float(v) for v in table['U_P10']][::-1]
    u_p90 = [float(v) for v in table['U_P90']][::-1]
    u_base = float(table['U_base'].iloc[0])
    labels_p10 = [f'{v:.0f}' for v in u_p10]
    labels_p90 = [f'{v:.0f}' for v in u_p90]

    p = figure(
        title='Tornado diagram: NPV sensitivity to each input variable',
        y_range=y_vars,
        width=750, height=420,
        x_axis_label='Utility',
        y_axis_label='Variable',
        # toolbar_location=None,
        background_fill_color='#fafafa',
    )

    # Bars: left = min(P10, P90), right = max(P10, P90). Negative-width
    # bars are not needed here because we take the bracket explicitly.
    left = [min(a, b) for a, b in zip(u_p10, u_p90)]
    right = [max(a, b) for a, b in zip(u_p10, u_p90)]
    p.hbar(
        y=y_vars, left=left, right=right,
        height=0.55,
        color='#6baed6', alpha=0.8,
        line_color='#08519c', line_width=1,
    )

    # Vertical reference line at the base (all-P50) utility.
    base_span = Span(
        location=u_base, dimension='height',
        line_color='firebrick', line_width=2, line_dash='dashed',
    )
    p.add_layout(base_span)
    p.add_layout(Label(
        x=u_base, y=len(y_vars) - 0.8,
        text=f'Base utility = {u_base:.0f}',
        text_color='firebrick', text_font_size='9pt', x_offset=4,
    ))
    

    # End-of-bar value labels (P10 on the left, P90 on the right).
    p.text(x=u_p10, y=y_vars, text=labels_p10, x_offset=-10,
        text_align='right', text_baseline='bottom',
        text_font_size='9pt', text_color='#08519c')
    p.text(x=u_p90, y=y_vars, text=labels_p90, x_offset=10,
        text_align='left', text_baseline='bottom',
        text_font_size='9pt', text_color='#08519c')

    p.grid.grid_line_alpha = 0.3
    return p

if __name__ == '__main__':
    if len(sys.argv) ==1:
        print(__doc__)
    elif sys.argv[1].strip() == '-t':
        HTML_FILE = 'tornado.html'
        test(HTML_FILE)
    else:
        file = sys.argv[1].strip()
        if not os.path.exists(file):
            print('Could not find file ', file)
            sys.exit()
        html_file = file.replace('.csv', '.html')
        p10_p90_df = pd.read_csv(file)
        p10_p90_df.set_index(p10_p90_df.columns[0], inplace=True)
        tornado_table = build_utility_table(p10_p90_df, test_utility)
        tornado_figure = plot_tornado(tornado_table)
        output_file(filename=html_file)
        show(tornado_figure)