#!/usr/bin/env python
"""
Extract specific variables from fixed-width NHANES mortality data files.
Variables: SEQN, MORTSTAT, PERMTH_EXM

Based on CDC NHANES Linked Mortality File 2019 format specification.
"""

import pandas as pd
import os

def extract_mortality_data(input_file, output_file):
    """
    Extract SEQN, MORTSTAT, and PERMTH_EXM from fixed-width mortality file.

    Column positions (0-indexed):
    - SEQN: columns 0-5
    - MORTSTAT: column 14
    - PERMTH_EXM: columns 42-45
    """

    # Column specifications for fixed-width file (0-indexed)
    colspecs = [
        (0, 5),      # SEQN (0-indexed positions 0-4)
        (14, 15),    # MORTSTAT (0-indexed position 14 only)
        (42, 45),    # PERMTH_EXM (0-indexed positions 42-44)
    ]

    colnames = ['SEQN', 'MORTSTAT', 'PERMTH_EXM']

    print(f"Reading fixed-width data from: {input_file}")
    print(f"Column specifications: {colspecs}")

    # Read the fixed-width file
    df = pd.read_fwf(
        input_file,
        colspecs=colspecs,
        names=colnames,
        dtype={'SEQN': str, 'MORTSTAT': str, 'PERMTH_EXM': str}
    )

    # Clean up whitespace
    df = df.apply(lambda x: x.str.strip() if x.dtype == 'object' else x)

    # Convert columns to numeric where appropriate
    df['SEQN'] = pd.to_numeric(df['SEQN'], errors='coerce')
    df['MORTSTAT'] = pd.to_numeric(df['MORTSTAT'], errors='coerce')
    df['PERMTH_EXM'] = pd.to_numeric(df['PERMTH_EXM'], errors='coerce')

    # Replace '.' (missing values) with NaN
    df = df.replace('.', pd.NA)
    df = df.replace('..', pd.NA)

    print(f"\nData shape: {df.shape}")
    print(f"\nFirst few rows:")
    print(df.head(10))

    print(f"\nData types:")
    print(df.dtypes)

    print(f"\nMissing values:")
    print(df.isnull().sum())

    print(f"\nBasic statistics:")
    print(df.describe())

    # Save to CSV
    df.to_csv(output_file, index=False)
    print(f"\nData saved to: {output_file}")

    return df

if __name__ == "__main__":
    # Process both mortality files if they exist
    data_dir = "data"
    input_files = [
        os.path.join(data_dir, "NHANES_2003_2004_MORT_2019_PUBLIC.dat"),
        os.path.join(data_dir, "NHANES_2005_2006_MORT_2019_PUBLIC.dat"),
    ]

    output_file = os.path.join(data_dir, "mortality_cleaned.csv")

    dfs = []
    for input_file in input_files:
        if os.path.exists(input_file):
            print(f"\n{'='*60}")
            print(f"Processing: {input_file}")
            print(f"{'='*60}")
            df = extract_mortality_data(input_file, None)
            dfs.append(df)
        else:
            print(f"File not found: {input_file}")

    # Combine all data if multiple files
    if dfs:
        combined_df = pd.concat(dfs, ignore_index=True)
        print(f"\n{'='*60}")
        print(f"Combined data from {len(dfs)} file(s)")
        print(f"{'='*60}")
        print(f"Combined shape: {combined_df.shape}")
        print(f"\nFirst few rows of combined data:")
        print(combined_df.head())

        # Save combined file
        combined_df.to_csv(output_file, index=False)
        print(f"\nCombined data saved to: {output_file}")

        # Verify output file exists
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"\n[OK] Output file verified!")
            print(f"  File: {output_file}")
            print(f"  Size: {file_size:,} bytes")
            print(f"  Records: {len(combined_df)}")
        else:
            print(f"\n[ERROR] Output file not created")
