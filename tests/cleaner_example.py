from pathlib import Path
from real_estate_toolkit.data.loader import DataLoader
from real_estate_toolkit.data.cleaner import Cleaner

# Load the data
loader = DataLoader(Path("/Users/Marti/Desktop/final_project/real_estate_toolkit/files/train.csv"))
data = loader.load_data_from_csv()

# Clean the data
cleaner = Cleaner(data)

# Rename columns to snake_case
cleaner.rename_with_best_practices()

# Replace NA values with None
cleaned_data = cleaner.na_to_none()

# Example: Print the first row to see the changes
print("First row after cleaning:")
for key, value in cleaned_data[0].items():
    print(f"{key}: {value}")