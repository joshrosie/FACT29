
# Alternative Baseline Methods

This document provides a description of the alternative baseline methods that were previously explored in our work. While these methods are not included in the final paper, they remain available in the implementation for further experimentation. Each method represents a different approach to negotiation dynamics and serves as a potential reference for evaluating multi-agent negotiation strategies.

Below is a detailed description of each baseline method:           

## Random Feasible Proposal
In this approach, the proposing player selects a random deal from its time-based set of feasible options. If no feasible deals exist, it falls back to its non time-based feasibility set. The randomness provides a diverse exploration of possible agreements, serving as a simple baseline for comparison. More details about the time-based set of feasible options are discussed below.

### Time-based utility threshold
The Time-based utility threshold is defined as:
$$
T_{p_i}(t) = 100 - (100 - \tau_{p_i}) \cdot \frac{t}{R+1}
$$
Where $ \tau_{p_i} $ is the player’s static threshold, $ R $ the number of rounds, and $ t $ is the current round. Agents use this formula to obtain their time-based threshold for each round and use it to obtain their time-based set of feasible options for this round. This pushes proposing players to gradually lower their demands over time, simulating concessions and creating a dynamic where initially non-feasible deals might become feasible for the proposing player in later rounds. Deal distance is measured using discrete Manhattan distance. All the Alternative Baseline Methods presented here, are using the time-based utility threshold instead of the normal one.


## Midline
The proposing player selects a deal in its feasibility set closest to the fixed "midpoint" sub-option in each issue's entire set of sub-options.  For example, if issue A's suboptions were A1, A2, and A3, A2 would be the "midpoint" option. The assumption is that deals near the "center" of the possible values are more acceptable to all parties. This strategy disregards player-specific preferences and utility structures.


## Previous-Proposal Proximity
In this approach, the proposer chooses a feasible deal closest to the previous round's proposal. This strategy mimics a negotiation style where gradual changes build consensus, fostering continuity. If no previous proposal exists, it defaults to the random approach.

## Multi-Sample Consensus
The Multi-Sample Consensus approach generates proposals by using collective preferences formed throughout the negotiation. A history consensus is constructed, which is the dimension-wise average of all previously proposed deals. The proposer randomly samples up to K feasible deals and selects the one closest to the history consensus. This promotes incremental agreement-building by steering proposals toward the collective preferences that have emerged over time.


## Frequency-Restricted Multi-Sample Consensus
This approach restricts the selection to the most frequently proposed sub-options (top_k) for each issue, tracked via a frequency counter. The proposer intersects this restricted set with their feasible set, narrowing the focus to commonly favored options. From this refined set, up to K deals are randomly sampled, and the proposer selects the one closest to the history consensus. This method drives convergence by combining historical trends with frequently preferred options.


## Two-Phase Negotiation
The two-phase approach combines exploration and exploitation to balance early discovery with later refinement. In Phase 1 (exploration), during the first fraction of rounds (defined by explore_ratio), the proposer uses the Multi-Sample Consensus method, which focuses on aligning proposals with the average of previously proposed deals to encourage collective convergence.
In Phase 2 (exploitation), for the remaining rounds, the proposer switches to the Frequency-Restricted Multi-Consensus method, prioritizing options that align with group preferences while still considering feasibility and consensus.
The final proposal by player 1 also uses the frequency-restricted method, ensuring the negotiation concludes with a focus on widely supported deals. This phased structure enables dynamic adaptation, starting with broad exploration and transitioning to a more targeted exploitation of group trends.
