equityinfo <- function(symbol, extract=NULL) {
    
    if (is.null(extract)) {
        ## interactive with list of info available
        out <- quantmod::getQuote(symbol, src='yahoo', what = quantmod::yahooQF())
    } else {
        out <- quantmod::getQuote(symbol, src='yahoo', what = quantmod::yahooQF(extract))
    }
    return(out)
}

## equityinfo('SPY')
## equityinfo('AAPL', extract='P/E Ratio')
## equityinfo('AAPL', extract=c('Name (Long)', 'P/E Ratio', 'Price/EPS Estimate Next Year', 'Price/Book', 'Dividend Yield'))

