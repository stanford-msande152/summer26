Course: MS&E 152 summer 2026
Sequence: Week 5, Lecture 1
Date: Monday, July 20th 2026
Topic: Introduction to Decision Analysis
#### Links:
Course website: https://stanford-msande152.github.io/summer26/
Canvas: https://canvas.stanford.edu/courses/228284

-----

# Title: Time and risk preference

### What you will learn

## Class schedule
- Lecture: Time and RIsk Preference
- About this class
- Short break
- Second lecture
- Class activity
- ----
Think of cases where you've had to face delay in gratification or risk of loss.  When these become substantial they weaken our preferences.  Both risk and time preference are intangibles, characteristic of a decision maker's preferences, and not determined directly from monetary analysis.  Since they both have dis-utility these two attributes are sometimes conflated and treated as one. In Decision Analysis our goal is to quantify these intangibles and incorporate them into a single consistent measure of utility used to compare alternatives.  This is a principled method to express intuitive judgments about risk. 


## I.  The confusion of time and risk preference

Both risk and delay decrease the value of a certain prospect. In market economics the same discounting formula can be used for both, however the origins in personal preference are distinct and not to be confused. 
#### TIme preference

If we compare having a prospect of value $V_0$ now at time = 0 compared to receiving it, at time  = 1, say a year from now, and we assume that there would be value to having the prospect during the current year, that incremental value $i$ as a fraction of $V_1$ implies we would prefer to have the prospect now rather than later. As a deterministic indifference relation:

$$ V_0 \sim V_1 + iV_1 = V_1(1+i) $$
In monetary terms, the decrease  in value over time with $i$ as the time preference rate is:

$$ \frac{V_0}{1+i} = V_1 $$
For instance, if someone has urgent needs they may be be willing to take on debt -- valuing the larger sum in the future equivalent to the immediate amount in the present.  If extreme this need can be exploited by unscrupulous lenders. 

An investor has the opposite incentive when faced with an investment opportunity They will forego consumption of current resources, if the return on setting the amount aside more than offsets their time preference. 

Conversely, someone may prefer to defer consumption of a perishable item, to receive a *smaller* quantity in the future. For example if a shipment of ripe strawberries can't be enjoyed and would go to waste if received now, one may prefer a smaller shipment in the future, when they can be consumed. 

Time discounting applies to attributes that have use over time, so it doesn't make sense to apply it to timeless prospects such as the earth's environment as a whole.  The future of our kids -- our progeny -- or of life itself cannot be discounted. 

#### Compounding

One applies different time-discounts for prospects that occur at different times in the future, usually making the benign assumption that the discount rate is constant per interval.  So if values are received over a sequence of periods, the *Net Present Value* of their sum is

$$ NPV = \sum_{i=0}^n V_i = V_0 + V_0 (1+i)^{-1} + V_0 (1+i)^{-2} \cdots = V_0\sum_{i=0}^n (1+i)^{-i}   $$

In comparison when considering an investment one is looking at a time in the future when value will have increased:  compound growth.   For net present value we are standing in the present and considering how the future is discounted. Given enough years, the results of compounding or correspondingly discounting are substantial.  A 10% per year discount over ten years is equivalent to a reduction of more than half -- to about 35%. 

Decreasing the interval used for compounding proportionally with the rate, increases the total return, but only to a point.  For instance, a  10% per year return compounded monthly is equivalent to a $(1 + 0.1/12)^{12} \approx 10.5\%...$ return.  The returns for finer and finer intervals quickly reach a limit, as shown by this standard equivalence from calculus $(1+x/n)^n = e^x$
#### Interest rate markets

Buying and selling investments in financial markets reveal market interest rates that are not necessarily the same as a decision maker's. There are markets where money and goods can be bought and sold at designated future times,  in addition to immediate ("spot") trades. An example are government bonds that promise to return a fixed amount in the future in exchange for an current investment. As opposed to one's personal discount rate, these bond markets provide a *market rate* for "risk-free"  investment returns.  Similarly within a company the rates the company pays for raising investment funds (the "cost of capital") comes from what investors will pay for them.  When a decision involves either buying or selling investments, these market rates are appropriate to use as the time discounting rate. 

When using market rates, one needs to distinguish between nominal rates, that are affected by inflation that decreases the value of the dollar. A *rate of return*  in constant value dollars is the nominal rate minus the rate of inflation. 

### II. Attitudes toward Risk

Risk
> An ambiguous term, used at times to mean uncertainty or just"probability of loss", or "expected value of loss", etc.  For clarity we speak of risk attitude that is a consequence of making distinctions between the probability distribution of a prospect, the utility measure applied to it, and the resulting risk premium.

#### Certainty equivalents

Roughly the certainty equivalent captures the is a person's perceived value for an uncertain prospect as compared to the prospect's expected value. Unlike utility, whose units are relative, certain equivalent is in the same units as expected value.   To express risk aversion the certain equivalent of an uncertain prospect are typically lower than the expected value, the difference known as the *risk premium.*

$$\text{Expected Value} - \text{Risk Premium} = \text{Certain Equivalent}$$

A person whose risk premium is zero is *risk neutral.*  It is possible to be risk preferring.  Our theory of rationality does not dictate one's risk attitude. 

#### Computing the certain equivalent
Fortunately since the utility function is a continuous increasing function, the certain equivalent is found by taking the inverse of the expected utility.  

.. computaton



> Inversion of a utility value into an indifferent dollar amount.  Differs from a dollar expected value because of the way that 1) probability distribution of outcomes and 2) Utility function curvature interact. 

Graphical example. 

A "convex - upward" (typically called "concave") utility function expresses risk aversion.  Risk neutral decision makers have linear utility functions, so that their expected value and certain equivalents are equal and their risk premiums are zero.

(See Primary Text Fig 3-23 ff)
(Why is Kim and Jane's utility different - do we need to convert to money to take this into account? Is it possible to assign risk preference to them.  Howard (3-28) : "We thus see that we cannot tell whether a person is risk-neutral or risk averse by observing the decision made in any situation that does not have only money as the value measure of each prospect"."'"


| Prospect              | Preference Probability | Dollar Value |
| --------------------- | ---------------------- | ------------ |
| Wind generation, base | 1                      | \$100        |
| Solar plant, base     | 0.95                   | \$90         |
| Battery storage, peak | 0.67                   | \$50         |
| Battery storage, base | 0.57                   | \$40         |
| Solar plan, peak      | 0.32                   | \$20         |
| Wind generation, peak | 0                      | \$0          |


#### Effect of wealth on the utility function 

Should risk aversion increase or decrease with wealth? 
#### Simplifying the utility function - Delta property

The effect of wealth, and the functional form of utility functions with this wealth-independent property. 

### What order to apply discounting, risk preference, and expectation? 

In a conventional cost-benefit analysis, one's result is a single monetary value. We need to take into consideration time discounting, risk preference and uncertainty, and possibly also the cost of information.  What is the correct order to apply these?

- Any adjustments to value such as the cost of information apply directly to the value of the terminal prospect.  Dollars to dollars. 
- Time preference via discounting applies to certain future prospects, so we apply a risk free discount rate to monetary values when they will occur, and make a risk adjustment using the utility function. 
- The certain discounted monetary amount is the input to the utility function, to express risk preference.
- Uncertainty is applied last, to the certain utility quantities, by taking expectation, assuring that utilities are not a function of the probabilities. 



## Class Activity

## Key terms

time preference, time value of money
compound rates
rate of return, discount rate
net present value

risk premium, risk aversion, risk tolerance, risk preference
certain equivalent

## Files, references

For a seminal contribution about incorporating intangibles such as risk in decision -making see
C. Spetzler, (1968) "The Development of a Corporate Risk Policy for Capital Investment Decisions" IEEE Transactions on Sys. Sci & Cyber, Vol. SSC-4, No. 3, 
in  1. R. Howard & J. Matheson (1983) [“Readings on Decision Analysis Vol 2.”](https://stanford-msande152.github.io/summer26/lit/pubs/1983-howard-readingsondecisionanalysis-v2.pdf) (“The Blue Book”) SDG.

## Curious?  Things to explore 

© John Mark Agosta & Stanford University