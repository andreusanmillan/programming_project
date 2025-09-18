from dataclasses import dataclass
from typing import Optional
from .houses import House
from .house_market import HousingMarket
from .types import Segment



@dataclass
class Consumer:
    id: int
    annual_income: float
    children_number: int
    segment: Segment
    house: Optional[House]
    savings: float = 0.0
    saving_rate: float = 0.3
    interest_rate: float = 0.05
    
    def compute_savings(self, years: int) -> None:
        """
        Calculate accumulated savings over time using a year-by-year approach.
        
        For each year:
        1. Add annual contribution from salary
        2. Apply interest to total amount
        
        Args:
            years (int): Number of years to calculate savings for
            
        Raises:
            ValueError: If years is negative
        """
        if years < 0:
            raise ValueError("Years cannot be negative")
        
        # Calculate annual contribution from income
        annual_contribution = self.annual_income * self.saving_rate
        
        # For each year:
        # 1. Add the annual contribution
        # 2. Apply interest to the total amount
        for _ in range(years):
            # Add annual contribution from salary
            self.savings += annual_contribution
            
            # Apply interest to total amount
            self.savings = self.savings * (1 + self.interest_rate)
        
        # Round to 2 decimal places
        self.savings = round(self.savings, 2)

    def buy_a_house(self, housing_market: HousingMarket) -> None:
        """
        Attempt to purchase a suitable house from the market.
        
        The method:
        1. Calculates maximum affordable price based on savings (assumed 20% down payment)
        2. Gets list of suitable houses based on segment and price range
        3. Selects and purchases the first available matching house
        
        Args:
            housing_market: HousingMarket instance containing available houses
        """
        if self.house is not None:
            return  # Consumer already owns a house
            
        # Assume 20% down payment required, so maximum price is 5x savings
        max_price = self.savings * 5
        
        # Get suitable houses based on consumer's segment and max price
        suitable_houses = housing_market.get_houses_that_meet_requirements(
            max_price=max_price,
            segment=self.segment
        )
        
        # Purchase first suitable house if any are available
        if suitable_houses:
            selected_house = suitable_houses[0]
            selected_house.sell_house()
            self.house = selected_house
            # Deduct down payment from savings
            self.savings -= selected_house.price * 0.2