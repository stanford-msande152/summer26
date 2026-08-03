### III.  Entropy - a measure of information

Information means a message or observation of something unknown.   Here we derive a measure of information quantity is solely a function of the probability distribution of its contents. 

Note:  A Bayes network is just a visualization of the chain rule -- a factorization of the joint probability of the probability model into the product of the conditional probabilities at each node. 

Multiplying probabilities is equivalent to adding log probabilities.  So if we decompose a joint probability into its terms, the log probability is just the sum of the (negative) logs of each term.  This is a additive quantity derived from a probability. For a probability distribution of a random event, we reduce this by taking expectation over each term - again creating a sum.  This expectation of log probabilities for an event is, for historical reasons, called the *entropy* of the distribution. It reduces a distribution to a single number. Using log to the base 2, it is in units of "bits." More "random" distributions have higher entropy. When a variable is observed and it's distribution collapses to a single value its entropy goes to zero. 

"Shannon information" - just probabilities. For any uncertainty, the number of distinctions and their  probability is all that matters.  Whether it is about word counts, or marbles doesn't matter. Entropy is the measure of Shannon information. So one could compute the "entropy reduction" of making an observation. 

#### Entropy- based approximations to VOI

Mutual information is a function of the probability distribution of two variables that indicates how much knowing one variable's value increases our information, (e.g. decreases our entropy of another. )

(Is there a simple demonstration that increasing partial information is monotonic for the VOI given a specific VOI problem?)
