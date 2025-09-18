from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Any
import csv

@dataclass
class DataLoader:
    """Class for loading and basic processing of real estate data."""
    data_path: Path
    
    def load_data_from_csv(self) -> List[Dict[str, Any]]:
        """Load data from CSV file into a list of dictionaries.
        
        Returns:
            List[Dict[str, Any]]: List where each item is a dictionary representing a row
                                 with column names as keys and cell values as values.
        
        Raises:
            FileNotFoundError: If the specified CSV file doesn't exist
            ValueError: If the CSV file is empty or malformed
        """
        if not self.data_path.exists():
            raise FileNotFoundError(f"CSV file not found at {self.data_path}")
            
        try:
            with open(self.data_path, 'r', newline='', encoding='utf-8') as file:
                # Create CSV reader with dictionary format
                reader = csv.DictReader(file)
                
                # Verify that file has headers
                if not reader.fieldnames:
                    raise ValueError("CSV file has no headers")
                
                # Convert all rows to dictionaries and store in list
                data = []
                for row in reader:
                    # Convert empty strings to None for better data handling
                    processed_row = {
                        key: (None if value == '' else value) 
                        for key, value in row.items()
                    }
                    data.append(processed_row)
                
                if not data:
                    raise ValueError("CSV file contains no data rows")
                    
                return data
                
        except csv.Error as e:
            raise ValueError(f"Error reading CSV file: {str(e)}")
    
    def validate_columns(self, required_columns: List[str]) -> bool:
        """Validate that all required columns are present in the dataset.
        
        Args:
            required_columns (List[str]): List of column names that must be present
            
        Returns:
            bool: True if all required columns are present, False otherwise
            
        Raises:
            FileNotFoundError: If the CSV file doesn't exist
            ValueError: If the CSV file is empty or malformed
        """
        try:
            # Open file and read headers only
            with open(self.data_path, 'r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                headers = next(reader, None)
                
                if not headers:
                    raise ValueError("CSV file has no headers")
                
                # Check if all required columns are in headers
                return all(col in headers for col in required_columns)
                
        except csv.Error as e:
            raise ValueError(f"Error reading CSV file: {str(e)}")