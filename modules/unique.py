import pandas as pd

def unique(mylist):
        # input a list or pandas column (e.g., df.col1)
        # output unique values in list in order they appeared in mylist
        if (type(mylist) == list) | (type(mylist) == pd.Series):
            # list provided to function
            uniq = list(dict.fromkeys(mylist))
        else:
            # something else was provided to function so return input as a list
            uniq = [mylist]
        return uniq
