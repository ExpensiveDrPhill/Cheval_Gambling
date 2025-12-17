# Wallet class - handles money and debt
class Wallet:
    def __init__(self, starting_cash, debt_amount):
        self.cash = starting_cash
        self.original_debt = debt_amount
        self.debt = debt_amount
        self.bet_amount = 0
        self.starting_cash = starting_cash
    
    # Check if player can afford bet
    def can_place_bet(self, amount):
        return amount > 0 and amount <= self.cash
    
    # Take bet from cash
    def place_bet(self, amount):
        if self.can_place_bet(amount):
            self.cash -= amount
            self.bet_amount = amount
            return True
        return False
    
    # Add winnings to cash
    def add_winnings(self, winnings):
        self.cash += winnings
    
    # Math for debt calculation
    def update_debt(self):
        cash_gained = self.cash - self.starting_cash
        self.debt = self.original_debt - cash_gained
        # Clamp debt between 0 and original debt
        self.debt = max(0, min(self.original_debt, self.debt))
    
    # Check if bankrupt
    def check_bankruptcy(self):
        return self.cash <= 0
    
    # Check if reached win target
    def has_reached_target(self, target):
        return self.cash >= target
    
    # Calculate bet amount from percentage
    def get_bet_percentage_amount(self, percentage):
        import math
        amount = math.floor(self.cash * (percentage / 100))
        if amount <= 0 and self.cash > 0:
            amount = 1
        if amount > self.cash:
            amount = self.cash
        return amount
    
    # Reset bet to zero
    def reset_bet(self):
        self.bet_amount = 0
