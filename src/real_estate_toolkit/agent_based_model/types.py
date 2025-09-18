from enum import Enum, auto

class Segment(Enum):
    FANCY = auto()      # House is new construction and house score is the highest
    OPTIMIZER = auto()  # Price per square foot is less than monthly salary
    AVERAGE = auto()    # House price is below the average housing market price