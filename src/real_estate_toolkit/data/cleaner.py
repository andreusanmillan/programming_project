from dataclasses import dataclass
from typing import Dict, List, Any
import re

@dataclass
class Cleaner:
    """Class for cleaning real estate data."""
    data: List[Dict[str, Any]]
    
    def _convert_to_snake_case(self, name: str) -> str:
        """Convert a column name to snake_case format.
        
        Examples:
            'TotalBsmtSF' -> 'total_bsmt_sf'
            'GarageArea' -> 'garage_area'
            '1stFlrSF' -> 'first_flr_sf'
            
        Args:
            name: The column name to convert
            
        Returns:
            The converted name in snake_case
        """
        # Handle special cases first (like 1st -> first)
        name = name.replace('1st', 'first')
        name = name.replace('2nd', 'second')
        name = name.replace('3rd', 'third')
        
        # Insert underscore between number and letter
        name = re.sub(r'(\d+)', r'_\1_', name)
        
        # Add spaces between camelCase words
        name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
        
        # Convert to lowercase, replace spaces/special chars with underscore
        name = name.lower()
        name = re.sub(r'[^a-z0-9]+', '_', name)
        
        # Remove leading/trailing underscores and collapse multiple underscores
        name = re.sub(r'^_+|_+$', '', name)
        name = re.sub(r'_+', '_', name)
        
        return name

    def rename_with_best_practices(self) -> None:
        """Rename the columns with best practices (snake_case).
        
        This method modifies the data in place, updating all dictionary keys
        to follow Python naming conventions.
        """
        if not self.data or not isinstance(self.data[0], dict):
            return
        
        # Get the keys from the first dictionary (column names)
        old_keys = list(self.data[0].keys())
        
        # Create mapping of old names to new names
        key_mapping = {key: self._convert_to_snake_case(key) for key in old_keys}
        
        # Update all dictionaries in the data list
        for item in self.data:
            # Create new dictionary with renamed keys
            renamed_item = {key_mapping[old_key]: value 
                          for old_key, value in item.items()}
            # Update the original dictionary
            item.clear()
            item.update(renamed_item)

    def na_to_none(self) -> List[Dict[str, Any]]:
        """Replace NA values with None in all dictionaries.
        
        This method handles various forms of NA values that might appear in the data:
        - 'NA' strings
        - 'N/A' strings
        - Empty strings
        - Whitespace-only strings
        
        Returns:
            A new list of dictionaries with NA values replaced by None
        """
        cleaned_data = []
        
        for item in self.data:
            cleaned_item = {}
            for key, value in item.items():
                # Check for various forms of NA values
                if isinstance(value, str):
                    # Strip whitespace and check if empty or NA
                    value_stripped = value.strip().upper()
                    if (not value_stripped or 
                        value_stripped == 'NA' or 
                        value_stripped == 'N/A'):
                        cleaned_item[key] = None
                    else:
                        cleaned_item[key] = value
                else:
                    cleaned_item[key] = value
            cleaned_data.append(cleaned_item)
        
        return cleaned_data