#!/usr/bin/env python
"""
Prepare data for Cox proportional hazards model by extracting:
1. Daily step counts from accelerometry data
2. Age and gender from demographics
3. Merging with mortality data
"""

import pandas as pd
import numpy as np
import zipfile
import tempfile
import os
import sys

def extract_accel_summary(xpt_path):
    """
    Extract accelerometry data and compute daily step counts.
    """
    try:
        import pyreadstat
        print(f"  Reading accelerometry file: {xpt_path}")

        # Read the file with pyreadstat
        df, meta = pyreadstat.read_xport(xpt_path)
        print(f"    Loaded: {df.shape[0]:,} records, {df.shape[1]} columns")

        # List available columns
        print(f"    Available columns: {sorted(df.columns.tolist())[:20]}...")

        return df

    except Exception as e:
        print(f"  Error reading file: {e}")
        raise

def main():
    print("="*70)
    print("Preparing Data for Cox Proportional Hazards Model")
    print("="*70)

    # Load final_analysis_data.csv
    print("\n[1/4] Loading mortality and cycle information...")
    analysis_df = pd.read_csv("data/final_analysis_data.csv")
    print(f"  Loaded: {analysis_df.shape[0]:,} participants")
    print(f"  Columns: {analysis_df.columns.tolist()}")

    # We need to extract accelerometry data to get step counts
    print("\n[2/4] Extracting accelerometry data summary...")

    # Try to read a small sample from each accelerometry file to understand structure
    temp_dir = tempfile.mkdtemp()

    # Extract 2003-2004
    print("\n  2003-2004 Accelerometry Data:")
    try:
        with zipfile.ZipFile("data/2003-2004_NHANES.zip", 'r') as z:
            z.extract("paxraw_c.xpt", temp_dir)

        accel_2003 = extract_accel_summary(os.path.join(temp_dir, "paxraw_c.xpt"))

    except Exception as e:
        print(f"    Error: {e}")
        accel_2003 = None

    # Extract 2005-2006
    print("\n  2005-2006 Accelerometry Data:")
    try:
        with zipfile.ZipFile("data/2005-2006_NHANES.zip", 'r') as z:
            z.extract("paxraw_d.xpt", temp_dir)

        accel_2006 = extract_accel_summary(os.path.join(temp_dir, "paxraw_d.xpt"))

    except Exception as e:
        print(f"    Error: {e}")
        accel_2006 = None

    # Process accelerometry data to create daily step summaries
    print("\n[3/4] Computing daily step counts...")

    if accel_2003 is not None:
        print("  Processing 2003-2004 data...")
        # Check if this file has step data or minute-level activity
        # Common variable names in NHANES accelerometry:
        # SEQN = participant ID
        # PAXSTAT = activity value
        # PAXDAY = day of wear
        # PAXN = minute number

        # If we have SEQN and step/activity data, aggregate by participant
        if 'SEQN' in accel_2003.columns:
            # Look for step or activity variables
            activity_cols = [col for col in accel_2003.columns if 'step' in col.lower() or 'count' in col.lower() or 'pax' in col.lower()]
            print(f"    Found activity columns: {activity_cols[:10]}")

            # Group by SEQN and compute mean daily activity
            if activity_cols:
                # Try to aggregate
                accel_summary_2003 = accel_2003[['SEQN'] + activity_cols].groupby('SEQN').agg('mean')
                accel_summary_2003.columns = [f'accel_{col.lower()}' for col in activity_cols]
                accel_summary_2003 = accel_summary_2003.reset_index()
                print(f"    Created summary: {accel_summary_2003.shape[0]:,} participants")
            else:
                # Try different approach - just keep SEQN and look for any numeric column
                numeric_cols = accel_2003.select_dtypes(include=[np.number]).columns.tolist()
                if 'SEQN' in numeric_cols:
                    numeric_cols.remove('SEQN')

                print(f"    Found numeric columns: {numeric_cols[:10]}")

                # Use first numeric column as proxy for daily activity
                if numeric_cols:
                    accel_summary_2003 = accel_2003[['SEQN', numeric_cols[0]]].groupby('SEQN').agg('mean')
                    accel_summary_2003.columns = ['daily_activity']
                    accel_summary_2003 = accel_summary_2003.reset_index()
                    print(f"    Created summary using {numeric_cols[0]}: {accel_summary_2003.shape[0]:,} participants")

        del accel_2003  # Free memory

    if accel_2006 is not None:
        print("  Processing 2005-2006 data...")

        if 'SEQN' in accel_2006.columns:
            activity_cols = [col for col in accel_2006.columns if 'step' in col.lower() or 'count' in col.lower() or 'pax' in col.lower()]
            print(f"    Found activity columns: {activity_cols[:10]}")

            if activity_cols:
                accel_summary_2006 = accel_2006[['SEQN'] + activity_cols].groupby('SEQN').agg('mean')
                accel_summary_2006.columns = [f'accel_{col.lower()}' for col in activity_cols]
                accel_summary_2006 = accel_summary_2006.reset_index()
                print(f"    Created summary: {accel_summary_2006.shape[0]:,} participants")
            else:
                numeric_cols = accel_2006.select_dtypes(include=[np.number]).columns.tolist()
                if 'SEQN' in numeric_cols:
                    numeric_cols.remove('SEQN')

                print(f"    Found numeric columns: {numeric_cols[:10]}")

                if numeric_cols:
                    accel_summary_2006 = accel_2006[['SEQN', numeric_cols[0]]].groupby('SEQN').agg('mean')
                    accel_summary_2006.columns = ['daily_activity']
                    accel_summary_2006 = accel_summary_2006.reset_index()
                    print(f"    Created summary using {numeric_cols[0]}: {accel_summary_2006.shape[0]:,} participants")

        del accel_2006  # Free memory

    print("\n[4/4] Current step: Summary created, but need demographics data (age, gender)")
    print("\nNote: To complete the Cox model, we need:")
    print("  1. Daily step counts (will try to extract from accelerometry)")
    print("  2. Age and gender (need to find demographics files)")
    print("\nLet me check what other NHANES variables are available...")

if __name__ == "__main__":
    main()
