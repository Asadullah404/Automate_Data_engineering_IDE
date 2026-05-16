# ==============================================================================
# FILE LOCATION: AutomateFlow_Studio/Custom_Scripts/add_logic_sheet.py
# ==============================================================================

import pandas as pd
import numpy as np

def apply_advanced_scoring(df):
    """
    This function will be dynamically imported and executed by the Engine.
    It takes the Pandas DataFrame mid-pipeline, modifies it, and returns it.
    """
    print("--> Custom Plugin Running: Executing advanced statistical logic.")
    
    # You can write whatever complex math you want here.
    # Example: If a column named 'Revenue' exists, calculate a score
    if 'Revenue' in df.columns:
        # Create a randomized normalized score based on Revenue
        df['Advanced_Score'] = (df['Revenue'] / df['Revenue'].max()) * 100
        df['Advanced_Score'] = df['Advanced_Score'].fillna(0).round(2)
        
    return df