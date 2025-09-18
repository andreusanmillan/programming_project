from enum import Enum
from dataclasses import dataclass
from typing import Optional
import math

class QualityScore(Enum):
    EXCELLENT = 5
    GOOD = 4
    AVERAGE = 3
    FAIR = 2
    POOR = 1

@dataclass
class House:
    id: int
    price: float
    area: float
    bedrooms: int
    year_built: int
    quality_score: Optional[QualityScore]
    available: bool = True
    
    def calculate_price_per_square_foot(self) -> float:
        """
        Calculate and return the price per square foot.
        
        Returns:
            float: Price per square foot rounded to 2 decimal places.
            
        Raises:
            ValueError: If area is 0 or negative.
        """
        if self.area <= 0:
            raise ValueError("Area must be greater than 0")
        
        price_per_sqft = self.price / self.area
        return round(price_per_sqft, 2)
    
    def is_new_construction(self, current_year: int = 2024) -> bool:
        """
        Determine if house is considered new construction (< 5 years old).
        
        Args:
            current_year (int): Current year for age calculation. Defaults to 2024.
            
        Returns:
            bool: True if house is less than 5 years old, False otherwise.
            
        Raises:
            ValueError: If year_built is greater than current_year or before 1800.
        """
        if self.year_built > current_year:
            raise ValueError("Year built cannot be in the future")
        if self.year_built < 1800:
            raise ValueError("Year built cannot be before 1800")
            
        age = current_year - self.year_built
        return age < 5
    
    def get_quality_score(self) -> None:
        """
        Generate a quality score based on house attributes if not already set.
        
        The score is calculated based on:
        - Age of the house (newer = better)
        - Size per bedroom (more space = better)
        - Base size (larger = better)
        
        Updates the quality_score property of the house.
        """
        if self.quality_score is not None:
            return
        
        # Calculate age score (0-1)
        current_year = 2024
        max_age = current_year - 1800  # Maximum reasonable age
        age = current_year - self.year_built
        age_score = 1 - (age / max_age)
        
        # Calculate size per bedroom score (0-1)
        avg_room_size = 200  # Average room size in square feet
        size_per_bedroom = self.area / max(1, self.bedrooms)  # Avoid division by zero
        size_score = min(1, size_per_bedroom / (avg_room_size * 2))  # Cap at 2x average
        
        # Calculate base size score (0-1)
        avg_house_size = 2000  # Average house size in square feet
        base_size_score = min(1, self.area / (avg_house_size * 2))  # Cap at 2x average
        
        # Combine scores with weights
        total_score = (age_score * 0.3) + (size_score * 0.4) + (base_size_score * 0.3)
        
        # Convert to quality score enum
        if total_score >= 0.8:
            self.quality_score = QualityScore.EXCELLENT
        elif total_score >= 0.6:
            self.quality_score = QualityScore.GOOD
        elif total_score >= 0.4:
            self.quality_score = QualityScore.AVERAGE
        elif total_score >= 0.2:
            self.quality_score = QualityScore.FAIR
        else:
            self.quality_score = QualityScore.POOR

    def sell_house(self) -> None:
        """
        Mark house as sold by setting available to False.
        """
        self.available = False