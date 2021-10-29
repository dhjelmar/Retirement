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
value  <- shares * price
weight <- value / sum(value)

## get twr for each asset
out <- equityget(asset, period='months')
twr <- xts::last(out$twr, n=12*5)

## get twr for the benchmark
out <- equityget('SPY', period='months')
SPY <- as.numeric( xts::last(out$twrbench$SPY,  n=12*5) )

## calculate beta for each asset
beta  <- NA
alpha <- NA
for (i in 1:length(asset)) {
    twr_asset <- as.numeric(twr[,i])
    out <- alpha_beta(twr_asset, SPY)$beta
    beta[i]  <- out$beta
    alpha[i] <- out$alpha
}
beta  <- as.data.frame( unlist(t(beta)) )
alpha <- as.data.frame( unlist(t(alpha)))
names(beta)  <- asset
names(alpha) <- asset

## calculate portfolio beta
beta_portfolio <- sum( weight * beta )
beta <- data.frame(beta, portfolio = beta_portfolio)
print(beta)
