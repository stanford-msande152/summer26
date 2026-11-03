---
layout: default
nav_exclude: true
---
# CDN solution by full enumeration. 

tl;dr 
: A moderate sized network can be solved by `SQL` operations on a list of the entire state space. 

A network of up to 20 nodes, of combined random discrete variables and discrete decisions, assumed binary is a manageable 2^20 ~= 1E6 states. By enumerating all states, the max expected utility can be solved by a set of sql operations on the list. The list consists of a row for each terminal outcome, by policy, that is each outcome is replicated for each decision x rv - level combination. Solution consists of taking expectations for each policy, then mazimizing over policy.  (Is this equiv to a large decn table? Then how are probs that depend on policy choices included?) 

The input table looks something like this

Header:
s1, s2, ..., d1, d2, ..., product of probs, outcome value. 

For risk aversion a risk odds or tolorance param is needed. 

FOr VOI and sensitivity a modified table is solved. 

The solution are the outcome lotteries by policy choice (a sorting of the table)

The solution reduces top a certain equivalent value for each policy option. 

How is the table modified to change decision order  to compute with or without info?  Just by relabeling the decision choices among the outcomes.  By reducing some rows to uniform choices then the "info" contained in that row is not known at the time of the decision. 

What is the algorithm to take the DAG of the CDN or the tree and convert it to the state enumeration list as input to the solver? Just walk the CDN in partial order, to respect the node conditionings, and enumerate all states.  This needs a table that encodes DAG partial ordering from which observability of states by decisions is computed. 
