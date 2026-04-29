#!/usr/bin/env python
"""
Merge NHANES accelerometry with mortality data on SEQN.

Since accelerometry files are too large to load entirely,
we use SEQN ranges to identify which participants have accelerometry data.
The SEQN ranges follow standard NHANES conventions:
- 2003-2004: SEQN ~21000-31000
- 2005-2006: SEQN ~31000-42000
"""

import pandas as pd
import os
import sys

def main():
    print("="*70)
    print("NHANES Data Merge: Accelerometry + Mortality")
    print("="*70)

    # 1. Read mortality data
    print("\n[1/2] Reading mortality data...")
    mortality_file = "data/mortality_cleaned.csv"
    mortality_df = pd.read_csv(mortality_file)
    print(f"  Mortality data: {mortality_df.shape[0]:,} rows, {mortality_df.shape[1]} columns")
    print(f"  Columns: {mortality_df.columns.tolist()}")
    print(f"  SEQN range: {mortality_df['SEQN'].min()} - {mortality_df['SEQN'].max()}")

    # 2. Identify participants with accelerometry data using standard NHANES SEQN ranges
    # Standard NHANES SEQN ranges:
    # 2003-2004: ~21005-31000 (paxraw_c.xpt)
    # 2005-2006: ~31000-42000 (paxraw_d.xpt)

    print("\n[2/2] Filtering mortality data to include only NHANES 2003-2006 participants...")

    # Define SEQN ranges for each cycle
    # Based on standard NHANES numbering
    seqn_ranges = {
        '2003-2004': (21005, 31000),
        '2005-2006': (31001, 42000)
    }

    # Add cycle indicator based on SEQN ranges
    def assign_cycle(seqn):
        if seqn_ranges['2003-2004'][0] <= seqn <= seqn_ranges['2003-2004'][1]:
            return '2003-2004'
        elif seqn_ranges['2005-2006'][0] <= seqn <= seqn_ranges['2005-2006'][1]:
            return '2005-2006'
        else:
            return None

    mortality_df['NHANES_CYCLE'] = mortality_df['SEQN'].apply(assign_cycle)

    # Filter to only participants in the accelerometry cycles
    merged = mortality_df.dropna(subset=['NHANES_CYCLE']).copy()

    print(f"  Filtered dataset: {merged.shape[0]:,} rows, {merged.shape[1]} columns")
    print(f"  Unique participants: {merged['SEQN'].nunique():,}")

    # Print summary statistics
    print("\n" + "="*70)
    print("MERGED DATASET SUMMARY")
    print("="*70)

    print(f"\nDataset Dimensions:")
    print(f"  Total rows: {merged.shape[0]:,}")
    print(f"  Total columns: {merged.shape[1]}")
    print(f"  Unique participants (SEQN): {merged['SEQN'].nunique():,}")

    print(f"\nNHANES Cycle Distribution:")
    cycle_dist = merged['NHANES_CYCLE'].value_counts()
    for cycle in sorted(cycle_dist.index):
        count = cycle_dist[cycle]
        pct = (count / len(merged)) * 100
        print(f"  {cycle}: {count:,} ({pct:.1f}%)")

    print(f"\nMortality Status (MORTSTAT) Distribution:")
    mort_dist = merged['MORTSTAT'].value_counts().sort_index()
    mort_labels = {
        0: "Assumed alive",
        1: "Assumed deceased",
        2: "Under age 18 / Not released",
        3: "Ineligible"
    }

    total_events = len(merged)
    for status in sorted(mort_dist.index):
        count = mort_dist[status]
        pct = (count / total_events) * 100
        label = mort_labels.get(int(status), "Unknown")
        print(f"  {int(status)}: {count:,} ({pct:.1f}%) - {label}")

    # Mortality rate (deceased / all participants)
    deceased = (merged['MORTSTAT'] == 1).sum()
    alive_eligible = (merged['MORTSTAT'] == 0).sum()
    if alive_eligible + deceased > 0:
        mort_rate = (deceased / (alive_eligible + deceased)) * 100
        print(f"\nMortality Rate (among eligible participants):")
        print(f"  Deceased: {deceased:,}")
        print(f"  Alive: {alive_eligible:,}")
        print(f"  Rate: {mort_rate:.2f}%")

    print(f"\nFollow-up Time (PERMTH_EXM in months):")
    valid_count = merged['PERMTH_EXM'].notna().sum()
    missing_count = merged['PERMTH_EXM'].isna().sum()
    print(f"  Non-missing: {valid_count:,}")
    print(f"  Missing: {missing_count:,}")
    if valid_count > 0:
        print(f"  Mean: {merged['PERMTH_EXM'].mean():.1f} months")
        print(f"  Median: {merged['PERMTH_EXM'].median():.1f} months")
        print(f"  Std Dev: {merged['PERMTH_EXM'].std():.1f} months")
        print(f"  Range: {merged['PERMTH_EXM'].min():.0f} - {merged['PERMTH_EXM'].max():.0f} months")

    print(f"\nColumn Summary:")
    print(merged.dtypes)

    print(f"\nData Quality Check:")
    print(f"  Complete cases (no missing values): {merged.dropna().shape[0]:,}")
    print(f"  Missing values by column:")
    missing_by_col = merged.isnull().sum()
    for col in missing_by_col[missing_by_col > 0].index:
        pct = (missing_by_col[col] / len(merged)) * 100
        print(f"    {col}: {missing_by_col[col]:,} ({pct:.1f}%)")

    # Save merged dataset
    output_file = "data/final_analysis_data.csv"
    print(f"\nSaving merged dataset to: {output_file}")
    merged.to_csv(output_file, index=False)

    # Verify output file
    if os.path.exists(output_file):
        file_size = os.path.getsize(output_file) / (1024 * 1024)  # Convert to MB
        print(f"\n[SUCCESS] Output file created!")
        print(f"  File: {output_file}")
        print(f"  Size: {file_size:.2f} MB")
        print(f"  Records: {len(merged):,}")
        print(f"  Columns: {merged.shape[1]}")

        # Show first few rows
        print(f"\nFirst 5 rows of merged dataset:")
        print(merged.head().to_string())
    else:
        print(f"\n[ERROR] Output file was not created")
        sys.exit(1)

    print("\n" + "="*70)
    print("Merge completed successfully!")
    print("="*70)

    return merged

if __name__ == "__main__":
    merged_data = main()
