Course: MS&E 152 summer 2026
Sequence: Week 4, Lecture 2
Date: Wednesday, July 15 2026
Topic: Introduction to Decision Analysis
#### Links:
Course website: https://stanford-msande152.github.io/summer26/
Canvas: https://canvas.stanford.edu/courses/228284

-----

# Title:  Party Problem -- value of information 

### What you will learn

## Class schedule
- Lecture
- About this class
- Short break
- Second lecture
- Class activity
- ----
## I. Solving for the "rain detector" value

The rain detector is a predictor that has a probability of 0.8 predicting rain or sun correctly, and a 0.2 probability of a "false negative" or "false positive" error. 

We can extend the analysis of VOI to consider the case where the predictor's accuracy is known, short of having complete information in the weather, our variable of interest. 

This analysis is best carried out directly on the CDN:
![](PP_detectorVOI_values.png)
Knowing the accuracy of the predictor draw the dependency from weather to detector. However there is no way to draw a decision tree that respects the direction of the network arrows.   To solve the network we need to infer 'weather' from the observed value of "Detector", by use of Bayes Rule.  This is shown in the diagram by reversing the direction of the conditioning arrow between the two nodes.  The updated probability on "Detector" and the expected values for each detector observation are snow in this diagram:

![](Solved_PP_detectorVOI.png)

Weighting the expected values for the two solutions by the detector "marginal" probabilities obtains the expected value with information:

$$ E[v] = 0.44* 72.72 + 0.56 * 48.57 = 59.2 $$

Therefore the VOI with the detector is 

$$ 59.2 - 48 = 11.2 $$



## II. Structuring information with Causal Decision Networks

The general form of the kinds of models 
![](annotated_CDN.png)

The parts of a CDN
![](submodels_CDN.png)

## II.  The posterior distribution 

A generalization of Bayes Rule. 

## III.  When information has value

When would the clairvoyant have a selling price for information.  

Why the VOI is never negative in a deciison problem. 

? Certainty equivalent of VOI. 


| Prospect              | Preference Probability | Dollar Value |
| --------------------- | ---------------------- | ------------ |
| Wind generation, base | 1                      | \$100        |
| Solar plant, base     | 0.95                   | \$90         |
| Battery storage, peak | 0.67                   | \$50         |
| Battery storage, base | 0.57                   | \$40         |
| Solar plan, peak      | 0.32                   | \$20         |
| Wind generation, peak | 0                      | \$0          |

### IV. Attitudes toward Risk

(See Primary Text Fig 3-23 ff)
(Why is Kim and Jane's utility different - do we need to convert to money to take this into account? Is it possible to assign risk preference to them.  Howard (3-28) : "We thus see that we cannot tell whether a person is risk-neutral or risk averse by observing the decision made in any situation that does not have only money as the value measure of each prospect"."'"

#### Simplifying the utility function - Delta property

The effect of wealth, and the functional form of utility functions with this wealth-independent property. 

## Class Activity

## Key terms


## Homework, due __ 

## Files, references

## Curious?  Things to explore 

© John Mark Agosta & Stanford University