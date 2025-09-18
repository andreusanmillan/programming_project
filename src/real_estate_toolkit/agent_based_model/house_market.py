from typing import List, Optional, Dict
from statistics import mean
from .houses import House, QualityScore
from .types import Segment


class HousingMarket:
    def __init__(self, houses: List[House]):
        """
        Initialize the housing market with a list of houses.
        
        Args:
            houses (List[House]): Initial list of houses in the market
        """
        self.houses = houses
        # Create an index for faster house lookups
        self._house_index: Dict[int, House] = {house.id: house for house in houses}
    
    def get_house_by_id(self, house_id: int) -> Optional[House]:
        """
        Retrieve specific house by ID.
        
        Args:
            house_id (int): The unique identifier of the house to retrieve
            
        Returns:
            Optional[House]: The house if found, None otherwise
        """
        return self._house_index.get(house_id)
    
    def calculate_average_price(self, bedrooms: Optional[int] = None) -> float:
        """
        Calculate average house price, optionally filtered by number of bedrooms.
        
        Args:
            bedrooms (Optional[int]): Number of bedrooms to filter by. If None, calculates
                                    average for all houses.
                                    
        Returns:
            float: Average price of houses meeting the criteria
            
        Raises:
            ValueError: If no houses match the criteria or if bedrooms is negative
        """
        if bedrooms is not None and bedrooms < 0:
            raise ValueError("Number of bedrooms cannot be negative")
            
        filtered_houses = [
            house for house in self.houses
            if house.available and (bedrooms is None or house.bedrooms == bedrooms)
        ]
        
        if not filtered_houses:
            raise ValueError(
                f"No available houses found{' with ' + str(bedrooms) + ' bedrooms' if bedrooms else ''}"
            )
            
        return mean(house.price for house in filtered_houses)
    
    def get_houses_that_meet_requirements(
        self, 
        max_price: float, 
        segment: Segment
    ) -> List[House]:
        """
        Filter houses based on buyer requirements.
        
        Args:
            max_price (float): Maximum price the buyer can afford
            segment (Segment): Buyer's market segment preference
            
        Returns:
            List[House]: List of houses meeting all requirements
            
        Raises:
            ValueError: If max_price is negative
        """
        if max_price <= 0:
            raise ValueError("Maximum price must be positive")
            
        matching_houses = []
        current_year = 2024  # Could be passed as parameter if needed
        
        for house in self.houses:
            if not house.available or house.price > max_price:
                continue
                
            # Apply segment-specific filters
            if segment == Segment.FANCY:
                if (not house.is_new_construction(current_year) or 
                    house.quality_score != QualityScore.EXCELLENT):
                    continue
            elif segment == Segment.OPTIMIZER:
                # Calculate price per square foot and compare to market average
                try:
                    house_price_per_sqft = house.calculate_price_per_square_foot()
                    market_avg_price = self.calculate_average_price()
                    market_avg_size = mean(h.area for h in self.houses if h.available)
                    market_price_per_sqft = market_avg_price / market_avg_size
                    if house_price_per_sqft >= market_price_per_sqft:
                        continue
                except (ValueError, ZeroDivisionError):
                    continue
            elif segment == Segment.AVERAGE:
                try:
                    market_avg_price = self.calculate_average_price()
                    if house.price > market_avg_price:
                        continue
                except ValueError:
                    continue
                    
            matching_houses.append(house)
            
        return matching_houses