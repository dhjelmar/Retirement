adjusted_price <- function(symbols, from, to=Sys.Date(), source='yahoo') {
    ## function returns a dataframe of adjusted prices
    ## e.g., adjusted_price(c("SPY","EFA", "IJS", "EEM","AGG"), from='2005-01-01')
                                        # The symbols vector holds our tickers. 

    ## install.packages('quantmod')

    ## Download historical info into dataframes with each symbol name.
    ## The last column from yahoo is the adjusted price.
    ## "While closing price merely refers to the cost of shares at the end of the day, 
    ##  the adjusted closing price considers other factors like dividends, stock splits, 
    ##  and new stock offerings. Since the adjusted closing price begins where the 
    ##  closing price ends, it can be called a more accurate measure of stocks' value"
    quantmod::getSymbols(symbols, 
                         src = source, 
                         from = from, 
                         to  = to,
                         auto.assign = TRUE, 
                         warnings = FALSE)
  
  ## following fails if some requested asset does not go back to the requested time
  ## need logic to replace with NA
  
    first    <- as.data.frame( get(symbols[1]) )
    adjprice <- data.frame( Date = rownames(first) )
    ncols    <- ncol(first)
    for (i in 1:length(symbols)) {
        temp <- as.data.frame( get(symbols[i]) )
        adjprice[i+1] <- temp[,ncols]
    }
    names(adjprice) <- c('Date', symbols)
    return(adjprice)
}
