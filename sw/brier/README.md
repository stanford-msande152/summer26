---
layout: default
title: "Brier"
nav_exclude: true
---
# A web page implementation for computing the Brier scores for a list of True-False questions

This is the instruction shown at the top of the page:

> This page displays a list of 36 items of numeric input widgets that accept percentage values between 1 and 99. If the user enters a value outside the range it is converted to the min or max allowable range. 

Alongside each item is displayed a logical value "True" or "False".  For each item it computes the Brier score for the inputted numeric value n, using this formula:

$$ (1/9604)*(n - v)^2$$ 

where v equals 1 for True items and 99 for False items. 

When values are entered for an item, the score is printed alongside it. A running average of the scores is shown at the top of the page.  

To configure the page one loads an answer file with a list of "T" or "F" values indicating if the item should be scored true or false. The user is prompted to upload an answer file before the enter values. 


