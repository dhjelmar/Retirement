equityget <- function(symbol, from, to=Sys.Date(), source='yahoo', period='daily') {
    ## function returns a dataframe of adjusted prices
    ## e.g., adjusted_price(c("SPY","EFA", "IJS", "EEM","AGG"), from='2005-01-01')
    ##       adjusted_price(c("SPY","EFA", "IJS", "EEM","AGG"), from='2005-01-01')

    ## install.packages('quantmod')

    ## Download historical info into dataframes with each symbol name.
    ## The last column from yahoo is the adjusted price.
    ## "While closing price merely refers to the cost of shares at the end of the day, 
    ##  the adjusted closing price considers other factors like dividends, stock splits, 
    ##  and new stock offerings. Since the adjusted closing price begins where the 
    ##  closing price ends, it can be called a more accurate measure of stocks' value"
    quantmod::getSymbols(symbol, 
                         src = source, 
                         from = from, 
                         to  = to,
                         auto.assign = TRUE, 
                         warnings = FALSE)

    ## index of an xts object is the date
    ## can access using zoo::index()
    ## dates <- as.Date( zoo::index( get(symbols[1]) ) )

    ## intersted in: prices which are the 4th column
    ##               adjusted prices which are the last column of each xts symbol object
    closeprice <- get(symbol[1])[,4]
    ncols      <- ncol( get(symbol[1]) )
    adjprice   <- get(symbol[1])[,ncols]
    ## merge adjusted prices for additional symbols, if any
    if (length(symbol) > 1) {
        for (i in 2:length(symbol)) {
            closeprice <- merge(closeprice, get(symbol[i])[,4])
            adjprice   <- merge(adjprice  , get(symbol[i])[,ncols])
        }
    }

    ## fix names and return
    names(adjprice) <- symbol

    ## adjust to monthly if requested
    if (period != 'daily') {
        closeprice <- xts::to.monthly(closeprice)
        adjprice   <- xts::to.monthly(adjprice)
    }

    ## convert to matrix until maybe someday if I learn xts
    closepricem <- as.matrix(closeprice)
    adjpricem <- as.matrix(adjprice)
    
    ## calculate return (I have not figured out xts operations so converting to matrix)
    nrows <- nrow(adjpricem)
    twr <- adjpricem[2:nrows,] / adjpricem[1:(nrows-1),] - 1
    
    return(list(close = closepricem, adjprice = adjpricem, twr=twr))
    }
