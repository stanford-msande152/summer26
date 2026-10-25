
# Adaptation of the Genie UX

Outcome lottery PMF display without transferring model to equation using monte carlo

Use point and interval values assigned to uncertain nodes for ALU & MLU utilities

## Critique on current DA methods and tools

- Extend IDs to the three sub models. 
- practical methods for Risk assessment
- Tornado diagrams - an obsolete heuristic for sensitivity
- Real time sensistivity interactive tools - e.g. on prob. dominance
- Extensions to Genie
	- Value nodes that show outcome lotteries - MAU and function node combination? 
	- VOI -- what is the algorithm?  How does it treat utility? Make it explicit on the diagram
	- Reformatting policy tables - vertically
	- A "Qgenie" type interface for CDN?
	- Move entirely to web for class? 
	- Default ( readable ) visual node formatting

	---
	This is a canonical model, where a decision both observes evidence and has an effect on the outcome.  

 Solving the network, the value (policy) tables condition on both the observation and the decision alternatives.  Conditioning on the observation states when the decision is determined is not intuitive, since the observation doesn't matter.  I think I understand how this comes about. Genie is using "Cooper88" as a solution method which simply iterates over all observable and decision states, hence the observation state stays in the iteration set even though it is no longer relevant to the decision.  
Is it possible to get the expected value given the best policy?  Maybe the iteration=based solution method does not reveal this.
Using the "Best pollicy" algorithm on this file gives an error - and may cause Genie to crash
What is the meaning of the VOI UX? There seem to be choices where the values are negative.  