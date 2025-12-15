"""
Wallet.py - Manages all financial logic for the game
Corresponds to the 'Uang' class in the project proposal
"""

class Wallet:
    """Handles all financial transactions and debt management."""
    
    def __init__(self, starting_cash, debt_amount):
        self.cash = starting_cash
        self.original_debt = debt_amount
        self.debt = debt_amount
        self.bet_amount = 0
        self.starting_cash = starting_cash
    
    def can_place_bet(self, amount):
        """Check if player has enough cash to place a bet."""
        return amount > 0 and amount <= self.cash
    
    def place_bet(self, amount):
        """Deduct bet amount from cash. Returns True if successful."""
        if self.can_place_bet(amount):
            self.cash -= amount
            self.bet_amount = amount
            return True
        return False
    
    def add_winnings(self, winnings):
        """Add winnings to cash."""
        self.cash += winnings
    
    def update_debt(self):
        """Calculate debt dynamically based on cash progress."""
        cash_gained = self.cash - self.starting_cash
        self.debt = self.original_debt - cash_gained
        # Clamp debt between 0 and original debt
        self.debt = max(0, min(self.original_debt, self.debt))
    
    def check_bankruptcy(self):
        """Check if player is bankrupt."""
        return self.cash <= 0
    
    def has_reached_target(self, target):
        """Check if player has reached the win target."""
        return self.cash >= target
    
    def get_bet_percentage_amount(self, percentage):
        """Calculate bet amount based on percentage of current cash."""
        import math
        amount = math.floor(self.cash * (percentage / 100))
        if amount <= 0 and self.cash > 0:
            amount = 1
        if amount > self.cash:
            amount = self.cash
        return amount
    
    def reset_bet(self):
        """Reset the current bet amount."""
        self.bet_amount = 0
