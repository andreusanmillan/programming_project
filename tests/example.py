# tests/example.py
from pathlib import Path
from real_estate_toolkit.data.loader import DataLoader

# Get the directory where our script is located
current_file = Path(__file__)  # __file__ tells us where this script is
project_root = current_file.parent.parent  # Go up two levels to reach project root
data_file = project_root / "files" / "train.csv"

def main():
    # Use a relative path that works from the project root
    data_path = Path(data_file)
    
    print(f"Trying to load data from: {data_path.absolute()}")
    
    # Create the loader
    loader = DataLoader(data_path=data_path)
    
    # Test if file exists
    if data_path.exists():
        print("✓ Found the data file!")
    else:
        print("✗ Could not find the data file!")
        print(f"  Make sure train.csv is in: {data_path.absolute()}")
        return

    # Test some basic columns
    test_columns = ["Id", "SalePrice"]
    if loader.validate_columns(test_columns):
        print("✓ Required columns are present!")
    else:
        print("✗ Some columns are missing!")

if __name__ == "__main__":
    main()