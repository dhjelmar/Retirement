import pandas as pd

def printall(df, width=1000):
    '''
    print entire dataframe
    '''

    # find default width and change it
    width_default = pd.get_option('display.width')
    pd.set_option('display.width', width) 

    # print all rows
    with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.max_colwidth', width):
        print(df)

    # reset default width
    pd.set_option('display.width', width_default) 