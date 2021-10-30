alpha_beta <- function(twr, twrbench, plot=FALSE, xlabel=NULL, ylabel=NULL, main=NULL) {

    ##-----------------------------------------------------------------------------
    ## pull label from the name of the vector if not specified otherwise
    if (is.null(xlabel)) xlabel   <- deparse(substitute(twrbench))
    if (is.null(ylabel)) ylabel   <- deparse(substitute(twr))

    ##-----------------------------------------------------------------------------
    ## fit return against benchmark and extract beta as slope and alpha as intercept
    if (isFALSE(plot)) {
         ## perform fit to find slope and intercept but do not make plot
         out <- lm(twr ~ twrbench)
         beta  <- out$coefficients[[2]]
         alpha <- out$coefficients[[1]]
    } else {
         out <- plotfit(xx = twrbench, yy = twr, xlab=xlabel, ylab=ylabel, main=main)
         beta  <- out$fits$slope
         alpha <- out$fits$intercept
    }

    ## alternate method to find beta
    ## beta <- cov(twr, twrbench) / var(twrbench)
    
    return(list(alpha=alpha, beta=beta))
}

## out <- equityget(c('SPY', 'AAPL'), period='months')
## extract last 5 years of monthly data
## AAPL <- as.numeric( xts::last(out$twr$AAPL, n=12*5) )
## SPY  <- as.numeric( xts::last(out$twr$SPY,  n=12*5) )
## alpha_beta(AAPL, SPY)
## alpha_beta(AAPL, SPY, plot=TRUE)
