Course: MS&E 152 summer 2026
Sequence: Week 1, Lecture 1
Date: Monday, June 22nd 2026
Topic: Introduction to Decision Analysis
#### Links:
Course website: https://stanford-msande152.github.io/summer26/
Canvas: https://canvas.stanford.edu/courses/228284

-----

# Title: Decision - Probability Tree operations

### What you will learn
What one can represent with Trees, and how to manipulate them. 
(This lecture follows the Primary Text Section 1.2 - 1.2.4)

## Class schedule
- Lecture
- About this class
- Short break
- Second lecture
- Class activity
- ----

## I.  Review of Decision - Probability  Trees

Tree root, branch, leaf, node, arc, terminal nodes, outgoing / incoming arcs
Correspondingly paths - trajectory, nodes - 3 kinds of events. Outcomes, previous and subsequent events. 
Labelling branches with events, choices, conditional probabilities
Labelling terminals with outcome values and elemental probabilities

[Image of the 3 node shapes]

Note: The common term is just _Decision Tree_

In a decision when is "do nothing" the complement to a choice? (The confusion in Quiz 2.)

## II.  The order of events in a tree.

What  is the meaning of changing orderings?  
- Changing conditionings of probabilities
- Changing information known at a decision, by placing the node for the earlier event  ("upstream of")  of the decision node.

Note: *Placing a node before another node does not necessarily mean that the information is "used" at a subsequent node!* As we saw, it is possible that the conditional probabilities on subsequent events are identical (e.g. do not depend) on each branch of a node. Sometimes the previous node is _relevant_ and sometimes not.  If two events are probabilistically independent (we usually just say "independent") of each other they are _irrelevant._

#### What it means to know something when making a decision

We speak of "having information" on which to base the decision.  Then the choice one makes is a function of the observed information at the time of the decision.  The event that is observed is just the state - the certain outcome of that event.  When a decision depends on knowing previous events the decision function is called a *policy.*

#### Common confusions between conditioning orderings

In natural language we often are not specific about the conditioning of probabilities when speaking of two  dependent ("correlated") events. We tend to be vague about the distinction. For instance when associating a headache, $H$ (a common occurrence) with brain tumors $B$ (a rare, serious diagnosis) there is a vast difference between and  $\mathsf{P}(H \ |\ B)$ -- a number close to 1 -- and $\mathsf{P}(B \ |\ H)$ -- a reassuringly rare possibility.    Just saying "headaches accompany brain tumors" is exasperatingly imprecise.  We need to use precise probability terms in such cases. 

#### "Flipping" conditionings

By probability algebra, we see a conditional probability's the two orderings are related: 

$$ \mathsf{P}(A \ |\ B)\mathsf{P}(B) =  \mathsf{P}(B \ |\ A)\mathsf{P}(A) $$
This expression is typically written as

$$ \mathsf{P}(A \ |\ B) =  \frac{\mathsf{P}(B \ |\ A)\mathsf{P}(A)}{\mathsf{P}(B)} $$
called _Bayes Rule. _

The calculation of Bayes Rule is equivalent to re-ordering two probability events in tree. Here's an example of "flipping" a two node tree. 

#### Relevance applies to both directions

#### Cause distinguishes direction of relevance

A simple example of thinking causally is when one event physically determines another.  "A dead car battery *causes* a car to not start. " "A fire reduces a log to ashes." More generally natural language is replete with causal references. "I'm starving so I want to eat now." In fact it is hard to imagine how we can express things without invoking cause.   Causal expressions go beyond just physical phenomena - they are a fundamental aspect of our understanding of the world. 

Explanations are typically expressed by referring to causes.  We often explain our belief about the appearance of B by claiming A caused it.  Knowing that fire causes smoke we can explain the appearance of smoke by the presence of a fire.  So when we seek an explanation we reach for a cause.  

For instance, a medical diagnosis determines the _cause_ of a set of symptoms. When the doctor explains a diagnosis they refer to what caused the symptoms. 

To be precise a cause can be encoded by a conditional probability, to express exactly how likely would the effect of the cause be observed. Hence in the process of constructing a probability to encode a belief, we may think about causes.  This of course is something we can capture in a probability tree!  However there is an important caution in associating causes and probabilities. Associations observed in data, such as statistical correlations may be consequences of a cause, but one cannot infer a causal connection just from such an association. The argument goes from cause to association, but not from association to concluding the existence of a cause.  This admonition is often stated as "Correlation does not imply causation."

## Class Activity

? Interval estimation ?

## Key terms

Decision Tree
Tree root, branch, leaf, node, arc, terminal nodes, outgoing / incoming arcs
paths - trajectory, nodes 
Outcomes, previous and subsequent events. 
conditional probabilities v/s elemental probabilities

relevant, 
irrelevant independent

observing information

Bayes Rule
## Homework2 , due July 6th 

## Files, references

## Curious?  Things to explore 

© John Mark Agosta & Stanford University