from typing import List, Dict, Any, Optional, Tuple
import polars as pl
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, mean_absolute_percentage_error
from pathlib import Path
import os

class HousePricePredictor:
    def __init__(self, train_data_path: str, test_data_path: str):
        """Initialize the predictor with training and test datasets."""
        self.train_data = pl.read_csv(
            train_data_path,
            null_values=['NA', 'None', '']
        )
        self.test_data = pl.read_csv(
            test_data_path,
            null_values=['NA', 'None', '']
        )
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.preprocessor = None
        self.models = {}

        # Store base path for later use
        self.base_path = Path(train_data_path).parent.parent


    def clean_data(self) -> None:
        """Perform comprehensive data cleaning on both training and test datasets."""
        def clean_dataset(df: pl.DataFrame) -> pl.DataFrame:
            # Calculate null ratios and drop columns with > 75% missing
            null_counts = df.null_count().row(0)
            total_rows = len(df)
            cols_to_drop = [
                col for col, count in zip(df.columns, null_counts) 
                if count / total_rows > 0.75
            ]
            
            if cols_to_drop:
                df = df.drop(cols_to_drop)
            
            # Identify numeric columns (except Id)
            dtypes = df.dtypes
            numeric_cols = [
                col for col, dtype in zip(df.columns, dtypes)
                if isinstance(dtype, (pl.Float64, pl.Float32, pl.Int64, pl.Int32, pl.Int16, pl.Int8)) 
                and col != 'Id'
            ]
            
            # Convert numeric columns to float
            for col in numeric_cols:
                df = df.with_columns(pl.col(col).cast(pl.Float64, strict=False))
            
            # Process categorical columns
            categorical_cols = [
                col for col in df.columns 
                if col not in numeric_cols and col != 'Id'
            ]
            
            # Convert categorical columns to string and handle nulls
            for col in categorical_cols:
                df = df.with_columns(pl.col(col).fill_null("None").cast(pl.Utf8))
            
            return df

        # Clean both datasets
        self.train_data = clean_dataset(self.train_data)
        self.test_data = clean_dataset(self.test_data)

    def prepare_features(self, target_column: str = 'SalePrice', 
                        selected_predictors: Optional[List[str]] = None) -> None:
        """Prepare datasets for machine learning."""
        if selected_predictors is None:
            selected_predictors = [
                col for col in self.train_data.columns 
                if col not in [target_column, 'Id']
            ]
        
        # Split features and target
        X_train = self.train_data.select(selected_predictors).to_pandas()
        y_train = self.train_data.select(target_column).to_pandas().values.ravel()
        X_test = self.test_data.select(selected_predictors).to_pandas()
        
        # Identify numeric and categorical columns
        numeric_features = X_train.select_dtypes(include=['int64', 'float64']).columns.tolist()
        categorical_features = X_train.select_dtypes(include=['object']).columns.tolist()
        
        # Create preprocessing pipelines
        numeric_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ])
        
        categorical_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
            ('onehot', OneHotEncoder(drop='first', sparse_output=False, handle_unknown='ignore'))
        ])
        
        # Combine preprocessing steps
        self.preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, numeric_features),
                ('cat', categorical_transformer, categorical_features)
            ])
        
        # Store processed data
        self.X_train = X_train
        self.X_test = X_test
        self.y_train = y_train

    def train_baseline_models(self) -> Dict[str, Dict[str, Any]]:
        """Train and evaluate baseline machine learning models."""
        results = {}
        
        models = {
            'Linear Regression': LinearRegression(),
            'Gradient Boosting': GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=4,
                random_state=42
            )
        }
        
        for name, model in models.items():
            pipeline = Pipeline([
                ('preprocessor', self.preprocessor),
                ('regressor', model)
            ])
            
            pipeline.fit(self.X_train, self.y_train)
            train_pred = pipeline.predict(self.X_train)
            
            metrics = {
                'MSE': mean_squared_error(self.y_train, train_pred),
                'MAE': mean_absolute_error(self.y_train, train_pred),
                'R2': r2_score(self.y_train, train_pred),
                'MAPE': mean_absolute_percentage_error(self.y_train, train_pred)
            }
            
            results[name] = {
                'metrics': metrics,
                'model': pipeline
            }
            self.models[name] = pipeline
        
        return results
    
    def forecast_sales_price(self, model_type: str = 'LinearRegression') -> None:
        """Generate predictions and create submission file."""
        if model_type not in self.models:
            raise ValueError(f"Model type {model_type} not found. Available models: {list(self.models.keys())}")
        
        predictions = self.models[model_type].predict(self.X_test)
        
        # Create submission dataframe
        submission = pl.DataFrame({
            'Id': self.test_data['Id'],
            'SalePrice': predictions
        })
        
        # Determine the absolute path for outputs
        # Start from where the data files are (files directory)
        # and create ml_models/outputs relative to that
        output_dir = self.base_path / 'src' / 'real_estate_toolkit' / 'ml_models' / 'outputs'
        print(f"Creating output directory at: {output_dir}")
        
        # Create directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Save the file
        output_file = output_dir / 'submission.csv'
        submission.write_csv(output_file)
        print(f"Saved submission file to: {output_file}")
        print(f"File exists: {output_file.exists()}") 