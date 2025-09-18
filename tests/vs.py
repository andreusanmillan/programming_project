from pathlib import Path
from real_estate_toolkit.data.loader import DataLoader
from real_estate_toolkit.data.cleaner import Cleaner
from real_estate_toolkit.data.descriptor import Descriptor
from real_estate_toolkit.data.descriptor_numpy import DescriptorNumpy

# Load and clean data
data_path = Path("/Users/Marti/Desktop/final_project/real_estate_toolkit/files/train.csv")
loader = DataLoader(data_path)
data = loader.load_data_from_csv()

# Clean the data
cleaner = Cleaner(data)
cleaner.rename_with_best_practices()
cleaned_data = cleaner.na_to_none()

# Create our NumPy descriptor
numpy_descriptor = DescriptorNumpy(cleaned_data)

# Let's analyze the sale price column
print("\nAnalyzing 'sale_price':")
print(f"Missing values ratio: {numpy_descriptor.none_ratio(['sale_price'])}")
print(f"Average: {numpy_descriptor.average(['sale_price'])}")
print(f"Median: {numpy_descriptor.median(['sale_price'])}")
print(f"75th percentile: {numpy_descriptor.percentile(['sale_price'], 75)}")
print(f"Type and mode: {numpy_descriptor.type_and_mode(['sale_price'])}")