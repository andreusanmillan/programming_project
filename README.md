# programming_project

## Real Estate Toolkit – Fixes & Notes

This document summarizes the issues found during testing and the modifications made to ensure the project runs smoothly.

## 1. Model Name Inconsistency

In main.py, the ML test used:

predictor.forecast_sales_price(model_type="Linear Regression")


However, in the original method definition:

def forecast_sales_price(self, model_type: str = 'LinearRegression'):
    """
    Args:
        model_type (str): Default is 'LinearRegression'. 
                          Other option is 'Advanced'.
    """


The mismatch caused errors during testing.

### Fix:

Unified model names to:

Linear Regression

Gradient Boosting

## 2. Data File Path Issues

The project could not locate data files due to the way paths were defined.

### Fix:

Updated file loading to use dynamic relative paths, ensuring compatibility across environments.

Example from main.py:

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "file.csv")

## 3. Circular Import in agent_based_model

The following error occurred:

ImportError: cannot import name 'HousingMarket' 
from partially initialized module ...

### Cause

consumers.py imports HousingMarket from house_market.py

house_market.py imports Segment from consumers.py

This created a circular import loop

### Fix

Created a new file types.py inside agent_based_model

Moved the Segment enum to types.py

Both consumers.py and house_market.py now import Segment from types.py

## Summary of Fixes
- Issue	Fix Applied
- Model name mismatch	Unified names → Linear
- Regression, Gradient Boosting
- Data file loading	
- Dynamic relative paths with os.path
- Circular import (ABM)	New types.py for Segment enum

With these changes, the project runs correctly and all tests execute without errors.
