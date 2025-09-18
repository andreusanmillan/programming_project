from dataclasses import dataclass
from typing import Dict, List, Tuple, Any, Union
import numpy as np
from collections import Counter

@dataclass
class DescriptorNumpy:
    """Class for calculating descriptive statistics of real estate data using NumPy."""
    data: List[Dict[str, Any]]

    def _is_numeric_string(self, value: Any) -> bool:
        """Helper method to check if a string can be converted to a number."""
        if value is None:
            return True
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False

    def _convert_to_numpy_array(self, column: str) -> Tuple[np.ndarray, bool]:
        """Convert a column of data into a NumPy array, handling None values.
        
        Args:
            column: Name of the column to convert
            
        Returns:
            Tuple of (numpy array, is_numeric flag)
        """
        values = [row[column] for row in self.data]
        
        # Check if values can be treated as numeric
        non_none_values = [v for v in values if v is not None]
        
        # Try converting to numeric if possible
        if all(self._is_numeric_string(v) for v in values):
            try:
                # Convert to float array, with np.nan for None values
                numeric_arr = np.array([np.nan if v is None else float(v) for v in values])
                return numeric_arr, True
            except (ValueError, TypeError):
                pass
        
        # If not numeric, return as object array
        return np.array(values, dtype=object), False

    def _validate_columns(self, columns: Union[List[str], str]) -> List[str]:
        """Validate column names and handle 'all' option."""
        if not self.data:
            raise ValueError("Data is empty")
            
        available_columns = list(self.data[0].keys())
        
        if columns == "all":
            return available_columns
        
        if isinstance(columns, str):
            columns = [columns]
        
        invalid_columns = [col for col in columns if col not in available_columns]
        if invalid_columns:
            raise ValueError(f"Invalid columns: {invalid_columns}")
        
        return columns

    def none_ratio(self, columns: Union[List[str], str] = "all") -> Dict[str, float]:
        """Compute the ratio of None values per column."""
        columns = self._validate_columns(columns)
        ratios = {}
        
        for col in columns:
            arr, _ = self._convert_to_numpy_array(col)
            none_count = np.sum(arr == None)
            ratios[col] = float(none_count / len(arr))
        
        return ratios

    def average(self, columns: Union[List[str], str] = "all") -> Dict[str, float]:
        """Compute the average value for numeric variables."""
        columns = self._validate_columns(columns)
        averages = {}
        
        for col in columns:
            arr, is_numeric = self._convert_to_numpy_array(col)
            if is_numeric:
                avg = np.nanmean(arr)
                if not np.isnan(avg):
                    averages[col] = float(avg)
        
        return averages

    def median(self, columns: Union[List[str], str] = "all") -> Dict[str, float]:
        """Compute the median value for numeric variables."""
        columns = self._validate_columns(columns)
        medians = {}
        
        for col in columns:
            arr, is_numeric = self._convert_to_numpy_array(col)
            if is_numeric:
                med = np.nanmedian(arr)
                if not np.isnan(med):
                    medians[col] = float(med)
        
        return medians

    def percentile(self, columns: Union[List[str], str] = "all", percentile: int = 50) -> Dict[str, float]:
        """Compute the percentile value for numeric variables."""
        if not 0 <= percentile <= 100:
            raise ValueError("Percentile must be between 0 and 100")
        
        columns = self._validate_columns(columns)
        percentiles = {}
        
        for col in columns:
            arr, is_numeric = self._convert_to_numpy_array(col)
            if is_numeric:
                perc = np.nanpercentile(arr, percentile)
                if not np.isnan(perc):
                    percentiles[col] = float(perc)
        
        return percentiles

    def type_and_mode(self, columns: Union[List[str], str] = "all") -> Dict[str, Tuple[str, Any]]:
        """Compute the type and mode for variables."""
        columns = self._validate_columns(columns)
        results = {}
        
        for col in columns:
            arr, is_numeric = self._convert_to_numpy_array(col)
            
            # Filter out None values
            valid_mask = arr != None
            valid_values = arr[valid_mask]
            
            if len(valid_values) == 0:
                continue
            
            if is_numeric:
                # For numeric values, handle nan values and find mode
                numeric_values = valid_values[~np.isnan(valid_values)]
                if len(numeric_values) > 0:
                    mode_value = float(Counter(numeric_values).most_common(1)[0][0])
                    results[col] = ('numeric', mode_value)
            else:
                # For categorical values, find the most common category
                mode_value = Counter(valid_values).most_common(1)[0][0]
                results[col] = ('categorical', mode_value)
        
        return results