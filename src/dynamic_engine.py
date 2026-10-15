import os
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score

DEFAULT_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "cropdata_updated.csv")
MODEL_PATH = os.path.join(os.path.dirname(__file__), "universal_pipeline.joblib")

def detect_column_roles(df):
    """
    Dynamically identifies target column, numeric feature columns, 
    and categorical feature columns from ANY uploaded dataset.
    """
    cols = list(df.columns)
    
    # 1. Detect target column
    target_candidates = ['result', 'target', 'label', 'class', 'irrigation', 'output', 'status', 'yield']
    target_col = None
    for cand in target_candidates:
        matches = [c for c in cols if cand.lower() in c.lower()]
        if matches:
            target_col = matches[0]
            break
            
    if not target_col:
        # Default to the last column as is standard in ML benchmarks
        target_col = cols[-1]

    feature_cols = [c for c in cols if c != target_col]
    
    # 2. Split into numeric and categorical
    numeric_cols = []
    categorical_cols = []
    
    for c in feature_cols:
        # If numeric dtype and has more than 10 unique values or is float
        if pd.api.types.is_numeric_dtype(df[c]):
            numeric_cols.append(c)
        else:
            categorical_cols.append(c)
            
    return target_col, numeric_cols, categorical_cols

def build_dynamic_pipeline(df, target_col=None):
    """
    Constructs, trains, and returns a dynamic ML pipeline adapted to the given dataset schema.
    """
    detected_target, numeric_cols, categorical_cols = detect_column_roles(df)
    if target_col is None or target_col not in df.columns:
        target_col = detected_target

    # Clean missing values
    df_clean = df.dropna(subset=[target_col]).copy()
    
    X = df_clean[numeric_cols + categorical_cols]
    y = df_clean[target_col]
    
    # Build column transformer
    transformers = []
    if numeric_cols:
        transformers.append(('num', StandardScaler(), numeric_cols))
    if categorical_cols:
        transformers.append(('cat', OneHotEncoder(handle_unknown='ignore'), categorical_cols))
        
    preprocessor = ColumnTransformer(transformers=transformers)
    
    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(n_estimators=80, max_depth=12, random_state=42))
    ])
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    pipeline.fit(X_train, y_train)
    
    acc = accuracy_score(y_test, pipeline.predict(X_test))
    
    meta = {
        "target_col": target_col,
        "numeric_cols": numeric_cols,
        "categorical_cols": categorical_cols,
        "classes": [str(c) for c in np.unique(y)],
        "accuracy": acc
    }
    
    return pipeline, meta

def load_default_pipeline():
    if os.path.exists(DEFAULT_DATA_PATH):
        df = pd.read_csv(DEFAULT_DATA_PATH)
        pipeline, meta = build_dynamic_pipeline(df, "result")
        return pipeline, meta, df
    return None, None, None
