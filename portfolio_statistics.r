## https://israeldi.github.io/bookdown/_book/monte-carlo-simulation-of-stock-portfolio-in-r-matlab-and-python.html


##-----------------------------------------------------------------------------
## setup
os <- .Platform$OS.type
if (os == 'windows') {
  ## load generic modules
  source("F:\\Documents\\01_Dave's Stuff\\Programs\\GitHub_home\\R-setup\\setup.r")
  ## identify working folder
  path <- c("f:/Documents/01_Dave's Stuff/Programs/GitHub_home/Retirement/")
} else {
  ## os == unix
  source('~/GitHub_repos/R-setup/setup.r')
  path <- c('~/GitHub_repos/Retirement/')
}
## set working folder
setwd(path)
## load local modules
r_files <- list.files(paste(path, 'modules/', sep=''), pattern="*.[rR]$", full.names=TRUE)
for (f in r_files) {
  ## cat("f =",f,"\n")
  source(f)
}

##-----------------------------------------------------------------------------
## Import data
data <- '
    AAPL           GOOG           FB
166.5791        1020.91       177.95
'
shares <- readall(data)
asset  <- names(shares)


##-----------------------------------------------------------------------------
## get price info
out <- equityinfo(asset, extract=c('Previous Close', 'P/E Ratio'))
price <- out$'P. Close'

## calculate value and weight of each asset
value      <- shares * price
totalvalue <- sum(value)
weight <- value / totalvalue

## get twr for each asset
out <- equityget(asset, period='months')
twr <- xts::last(out$twr, n=12*5)

## get twr for the benchmark
out <- equityget('SPY', period='months')
SPY <- as.numeric( xts::last(out$twr$SPY,  n=12*5) )

## calculate alpha and beta for each asset
beta  <- NA
alpha <- NA
for (i in 1:length(asset)) {
    twr_asset <- as.numeric(twr[,i])
    out <- alpha_beta(twr_asset, SPY)
    beta[i]  <- out$beta
    alpha[i] <- out$alpha
}
stats <- data.frame(asset, 
                    shares = as.numeric(shares), 
                    value=as.numeric(value), 
                    beta, 
                    alpha)

## calculate portfolio beta
beta_portfolio  <- sum( weight * beta )
alpha_portfolio <- sum( weight * alpha )
portfolio <- data.frame(asset  = 'portfolio', 
               shares = NA, 
               value  = totalvalue, 
               beta   = beta_portfolio,
               alpha  = alpha_portfolio)
stats <- as_tibble( rbind(stats, portfolio) )
print(stats)

## plot portfolio
out <- plotfit(stats$beta, stats$alpha, stats$asset, nofit=TRUE)
xx <- stats[nrow(stats),]$beta
yy <- stats[nrow(stats),]$alpha
color <- as.character(out$legend[nrow(out$legend),]$color)
points(xx, yy, pch=16, col=color)

## plot interactive
if (os == 'windows') {
    ## following uses plotly which does not work on Chromebook
    plot_interactive(stats, 'beta', 'alpha')
}

library(shiny)
shinyplot(as.data.frame(stats), 'beta', 'alpha')
