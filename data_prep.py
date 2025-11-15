import pandas as pd

def clean_and_dedupe_draws(input_file, output_file="hit5_clean_deduped.csv"):
    """
    Reads in raw draw CSV, cleans data types, sorts draws, removes duplicates, and saves results.
    Input must contain columns: ['DrawDate', 'Num1', 'Num2', 'Num3', 'Num4', 'Num5']
    """

    # Load raw data
    df = pd.read_csv(input_file)

    # Ensure number columns are integers and sort them for consistency
    num_cols = ['Num1', 'Num2', 'Num3', 'Num4', 'Num5']
    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df[num_cols] = df[num_cols].apply(lambda row: sorted(row), axis=1, result_type='broadcast')

    # Drop rows with missing Num columns
    df.dropna(subset=num_cols, inplace=True)

    # Remove duplicate draws (by all five numbers, regardless of order)
    df['draw_tuple'] = df[num_cols].apply(lambda row: tuple(sorted(row)), axis=1)
    df = df.drop_duplicates(subset=['draw_tuple'])

    # Sort by date if available, newest first
    if 'DrawDate' in df.columns:
        df['DrawDate'] = pd.to_datetime(df['DrawDate'], errors='coerce')
        df = df.sort_values('DrawDate', ascending=False)

    # Drop temporary column before saving
    df.drop('draw_tuple', axis=1, inplace=True)

    # Save cleaned deduped file
    df.to_csv(output_file, index=False)
    print(f"Cleaned and deduped file written to {output_file} (total draws: {len(df)})")

    return output_file, len(df)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Clean and dedupe Hit 5 lottery CSV files.")
    parser.add_argument("input_file", help="Path to raw draw CSV file")
    parser.add_argument("--output_file", help="Path to cleaned output CSV file", default="hit5_clean_deduped.csv")
    args = parser.parse_args()
    clean_and_dedupe_draws(args.input_file, args.output_file)
