"""
This file is for the multi-arm bandit model used for mutation. 
"""

import numpy as np

class NormalizedExponentialWeighting:
    """
    An MAB implementation. 
    """
    def __init__(self, 
                 strategies: list, 
                 learning_rate: float = 0.05):
        """
        The way of initialize should be the same. 
        """
        self.strategies = strategies
        self.eta = learning_rate
        self.n = len(strategies)
        self.weights = np.ones(self.n)  # Initialize all weights to 1
        self.weights /= np.sum(self.weights)  # normalize

    def select_strategy(self):
        """Return the strategy according to the weights."""
        chosen_idx = np.random.choice(self.n, p=self.weights)
        return self.strategies[chosen_idx]

    def update_weights(self, chosen_strategy, feedback: bool):
        """
        Update the weight and normalize immediately.
        `feedback` means the result of the strategy is positive or not. 
        """
        chosen_idx = self.strategies.index(chosen_strategy)
        if feedback:
            self.weights[chosen_idx] *= np.exp(self.eta)
        else:
            self.weights[chosen_idx] *= np.exp(-self.eta)
        self.weights /= np.sum(self.weights)  # Normalization
