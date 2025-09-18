from enum import Enum, auto
from dataclasses import dataclass
from random import gauss, randint, shuffle, choice
from typing import List, Dict, Any
from .houses import House, QualityScore
from .house_market import HousingMarket
from .consumers import Segment, Consumer

class CleaningMarketMechanism(Enum):
    INCOME_ORDER_DESCENDANT = auto()
    INCOME_ORDER_ASCENDANT = auto()
    RANDOM = auto()

@dataclass
class AnnualIncomeStatistics:
    minimum: float
    average: float
    standard_deviation: float
    maximum: float

@dataclass
class ChildrenRange:
    minimum: float = 0
    maximum: float = 5

@dataclass
class Simulation:
    housing_market_data: List[Dict[str, Any]]
    consumers_number: int
    years: int
    annual_income: AnnualIncomeStatistics
    children_range: ChildrenRange
    cleaning_market_mechanism: CleaningMarketMechanism
    down_payment_percentage: float = 0.2
    saving_rate: float = 0.3
    interest_rate: float = 0.05
    
    def create_housing_market(self) -> None:
        """
        Initialize market with houses from the provided data.
        
        This method:
        1. Converts raw data to House objects
        2. Validates required fields
        3. Creates a HousingMarket instance
        """
        houses: List[House] = []
        
        for idx, data in enumerate(self.housing_market_data):
            try:
                # Convert quality score (assuming overall_qual in data is 1-10)
                quality_score = None
                if 'overall_qual' in data:
                    score_value = int(data['overall_qual'])
                    # Map 1-10 to QualityScore (1-2 -> POOR, 3-4 -> FAIR, etc.)
                    if score_value <= 2:
                        quality_score = QualityScore.POOR
                    elif score_value <= 4:
                        quality_score = QualityScore.FAIR
                    elif score_value <= 6:
                        quality_score = QualityScore.AVERAGE
                    elif score_value <= 8:
                        quality_score = QualityScore.GOOD
                    else:
                        quality_score = QualityScore.EXCELLENT
                
                house = House(
                    id=idx,
                    price=float(data['sale_price']),
                    area=float(data['gr_liv_area']),
                    bedrooms=int(data['bedroom_abv_gr']),
                    year_built=int(data['year_built']),
                    quality_score=quality_score,
                    available=True
                )
                houses.append(house)
            except (KeyError, ValueError) as e:
                print(f"Skipping invalid house data: {e}")
                continue
        
        self.housing_market = HousingMarket(houses)

    def create_consumers(self) -> None:
        """
        Generate consumer population with randomized attributes.
        
        This method:
        1. Creates consumers_number of consumers
        2. Assigns random annual income using normal distribution
        3. Assigns random number of children
        4. Assigns random market segment
        5. Sets initial financial parameters
        """
        consumers: List[Consumer] = []
        
        for i in range(self.consumers_number):
            # Generate annual income using truncated normal distribution
            while True:
                income = gauss(self.annual_income.average, self.annual_income.standard_deviation)
                if self.annual_income.minimum <= income <= self.annual_income.maximum:
                    break
            
            # Generate random number of children
            children = randint(int(self.children_range.minimum), int(self.children_range.maximum))
            
            # Randomly select a market segment
            segment = choice(list(Segment))
            
            consumer = Consumer(
                id=i,
                annual_income=income,
                children_number=children,
                segment=segment,
                house=None,
                savings=0.0,  # Initial savings will be computed later
                saving_rate=self.saving_rate,
                interest_rate=self.interest_rate
            )
            consumers.append(consumer)
        
        self.consumers = consumers
    
    def compute_consumers_savings(self) -> None:
        """
        Calculate savings for all consumers over the simulation period.
        
        This method applies the saving rate and interest rate over the specified
        number of years for each consumer.
        """
        if not hasattr(self, 'consumers'):
            raise RuntimeError("Consumers must be created before computing savings")
            
        for consumer in self.consumers:
            consumer.compute_savings(self.years)

    def clean_the_market(self) -> None:
        """
        Execute market transactions according to the specified mechanism.
        
        This method:
        1. Orders consumers based on cleaning_market_mechanism
        2. Attempts purchase for each consumer in order
        """
        if not hasattr(self, 'consumers') or not hasattr(self, 'housing_market'):
            raise RuntimeError("Both consumers and housing market must be initialized")
        
        # Create a copy of consumers list to sort
        consumers_to_process = self.consumers.copy()
        
        # Apply the specified market cleaning mechanism
        if self.cleaning_market_mechanism == CleaningMarketMechanism.INCOME_ORDER_DESCENDANT:
            consumers_to_process.sort(key=lambda x: x.annual_income, reverse=True)
        elif self.cleaning_market_mechanism == CleaningMarketMechanism.INCOME_ORDER_ASCENDANT:
            consumers_to_process.sort(key=lambda x: x.annual_income)
        elif self.cleaning_market_mechanism == CleaningMarketMechanism.RANDOM:
            shuffle(consumers_to_process)
        
        # Process each consumer's attempt to buy a house
        for consumer in consumers_to_process:
            consumer.buy_a_house(self.housing_market)
    
    def compute_owners_population_rate(self) -> float:
        """
        Compute the proportion of consumers who own houses.
        
        Returns:
            float: Percentage of consumers who own houses (0 to 1)
        """
        if not hasattr(self, 'consumers'):
            raise RuntimeError("Consumers must be created before computing ownership rate")
            
        owners = sum(1 for consumer in self.consumers if consumer.house is not None)
        return owners / len(self.consumers)
    
    def compute_houses_availability_rate(self) -> float:
        """
        Compute the proportion of houses that are still available.
        
        Returns:
            float: Percentage of houses that are available (0 to 1)
        """
        if not hasattr(self, 'housing_market'):
            raise RuntimeError("Housing market must be created before computing availability rate")
            
        available = sum(1 for house in self.housing_market.houses if house.available)
        return available / len(self.housing_market.houses)