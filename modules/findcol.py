def findcol(df, first):
    '''
    input:  df = dataframe
            first = list of columns to put first
    output: reordered dataframe
    '''

    # Get the remaining columns
    remaining_cols = [col for col in df.columns if col not in first]

    # Create the new column order
    new_column_order = first + remaining_cols

    # Reindex the DataFrame with the new order
    df = df[new_column_order]

    return df