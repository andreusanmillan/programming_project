from typing import List, Dict
import polars as pl
import plotly.express as px
import plotly.graph_objects as go
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUTPUT_DIR = os.path.join(project_root, "src", "real_estate_toolkit", "analytics", "outputs")

# Create directory if it doesn't exist (including all parent directories)
os.makedirs(OUTPUT_DIR, exist_ok=True)


class MarketAnalyzer:
    def __init__(self, data_path: str):
        """
        Initialize the analyzer with data from a CSV file.
        Args:
            data_path (str): Path to the Ames Housing dataset.
        """
        # Modified data loading to handle NA values
        self.real_state_data = pl.read_csv(
            data_path,
            null_values=["NA", ""],  # Treat both "NA" and empty strings as null
            infer_schema_length=10000  # Increase schema inference length
        )
        self.real_state_clean_data = None

    def clean_data(self) -> None:
        """
        Perform data cleaning:
        - Handle missing values.
        - Convert columns to appropriate data types.
        - Assign cleaned data to self.real_state_clean_data.
        """
        # Filling missing numeric values with the column median
        numeric_columns = [
            col for col in self.real_state_data.columns 
            if self.real_state_data[col].dtype in [pl.Float32, pl.Float64, pl.Int32, pl.Int64]
        ]
        for col in numeric_columns:
            self.real_state_data = self.real_state_data.with_columns(
                pl.col(col).fill_nan(self.real_state_data[col].median())
            )

        # Fill missing categorical values with a placeholder
        categorical_columns = [
            col for col in self.real_state_data.columns 
            if self.real_state_data[col].dtype == pl.Utf8
        ]
        for col in categorical_columns:
            self.real_state_data = self.real_state_data.with_columns(
                pl.col(col).fill_null("Unknown")
            )

        # Assign cleaned data to the class variable
        self.real_state_clean_data = self.real_state_data

    def generate_price_distribution_analysis(self) -> pl.DataFrame:
        """
        Analyze sale price distribution using clean data.
        - Compute basic price statistics.
        - Create an interactive histogram of sale prices.
        - Save the histogram as an HTML file.
        """
        if self.real_state_clean_data is None:
            raise ValueError("Data must be cleaned before analysis.")

        # Compute statistics
        price_statistics = self.real_state_clean_data.select([
            pl.col("SalePrice").mean().alias("Mean"),
            pl.col("SalePrice").median().alias("Median"),
            pl.col("SalePrice").std().alias("Standard Deviation"),
            pl.col("SalePrice").min().alias("Minimum"),
            pl.col("SalePrice").max().alias("Maximum"),
        ])

        # Create histogram
        fig = px.histogram(
            self.real_state_clean_data.to_pandas(), 
            x="SalePrice", 
            title="Sale Price Distribution",
            labels={"SalePrice": "Sale Price"},
            nbins=50
        )
        fig.update_layout(bargap=0.1)
        output_path = os.path.join(OUTPUT_DIR, "sale_price_distribution.html")
        fig.write_html(output_path)

        # Save with error handling
        output_path = os.path.join(OUTPUT_DIR, "sale_price_distribution.html")
        try:
            fig.write_html(output_path)
            print(f"Successfully saved histogram to: {output_path}")
            # Verify file exists and has content
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                print(f"File created successfully with size: {os.path.getsize(output_path)} bytes")
            else:
                print("Warning: File was not created properly")
        except Exception as e:
            print(f"Error saving histogram: {str(e)}")

        return price_statistics

    def neighborhood_price_comparison(self) -> pl.DataFrame:
        """
        Create a boxplot comparing house prices across neighborhoods.
        - Calculate neighborhood-level statistics.
        - Save the boxplot as an HTML file.
        """
        if self.real_state_clean_data is None:
            raise ValueError("Data must be cleaned before analysis.")

        # Group by neighborhood and compute statistics
        neighborhood_stats = self.real_state_clean_data.groupby("Neighborhood").agg([
            pl.col("SalePrice").mean().alias("Mean"),
            pl.col("SalePrice").median().alias("Median"),
            pl.col("SalePrice").std().alias("Standard Deviation"),
        ])

        # Create boxplot
        fig = px.box(
            self.real_state_clean_data.to_pandas(), 
            x="Neighborhood", 
            y="SalePrice",
            title="Neighborhood Price Comparison",
            labels={"Neighborhood": "Neighborhood", "SalePrice": "Sale Price"}
        )
        fig.update_layout(xaxis_tickangle=-45)
        output_path = os.path.join(OUTPUT_DIR, "neighborhood_price_comparison.html")
        fig.write_html(output_path)

        print(f"Neighborhood price comparison boxplot saved at: {output_path}")
        return neighborhood_stats

    def feature_correlation_heatmap(self, variables: List[str]) -> None:
        """
        Generate a correlation heatmap for selected numerical variables.
        - Save the heatmap as an HTML file.
        Args:
            variables (List[str]): List of numerical variables to correlate.
        """
        if self.real_state_clean_data is None:
            raise ValueError("Data must be cleaned before analysis.")

        # Compute correlation matrix
        correlation_matrix = (
            self.real_state_clean_data.select(variables).to_pandas().corr()
        )

        # Create heatmap
        fig = px.imshow(
            correlation_matrix, 
            text_auto=True, 
            title="Feature Correlation Heatmap"
        )
        output_path = os.path.join(OUTPUT_DIR, "feature_correlation_heatmap.html")
        fig.write_html(output_path)

        print(f"Feature correlation heatmap saved at: {output_path}")

    def create_scatter_plots(self) -> Dict[str, go.Figure]:
        """
        Create scatter plots exploring relationships between key features.
        - Save each scatter plot as an HTML file.
        Returns:
            Dictionary of Plotly Figure objects.
        """
        if self.real_state_clean_data is None:
            raise ValueError("Data must be cleaned before analysis.")

        scatter_plots = {}
        plots_info = [
            ("SalePrice", "GrLivArea", "Price vs. Total Living Area"),
            ("SalePrice", "YearBuilt", "Price vs. Year Built"),
            ("SalePrice", "OverallQual", "Price vs. Overall Quality")
        ]

        for y, x, title in plots_info:
            fig = px.scatter(
                self.real_state_clean_data.to_pandas(),
                x=x, y=y,
                title=title,
                trendline="ols",
                labels={x: x, y: y},
                color="Neighborhood"
            )
            output_file = f"{x.lower()}_vs_{y.lower()}.html".replace(" ", "_")
            output_path = os.path.join(OUTPUT_DIR, output_file)
            fig.write_html(output_path)
            print(f"Scatter plot saved at: {output_path}")
            scatter_plots[title] = fig

        return scatter_plots