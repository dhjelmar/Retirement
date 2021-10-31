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

## ## example
## data <- '
## asset  shares
## AAPL      166
## GOOG     1021
## FB        178
## '
## data_in <- readall(data)
##
## ## convert data to vectors
## asset   <- as.character(data_in$asset)
## shares  <- data_in$shares

## define duration in years to use for beta and alpha
duration = 5

data <- readall('all.xlsx', sheet="Assets + Liabilities")


## delete non-security info (dlh remove this once clean xlsx)
data <- data[ (data$Account_Type == '401k (Flour)' &
               data$Account_Type == 'Bank' &
               data$Account_Type == 'Credit cards' &
               data$Account_Type == 'Primary home' &
               data$Account_Type == 'Vacation home'),]
data <- data[(data$Holding      != 'SCGE1' &
               data$Holding      != 'SCGI1' &
               data$Holding      != 'SCGL1' &
               data$Holding      != 'SCGN1' &
               data$Holding      != 'SCGS1' &
               data$Holding      != 'SCII1'),]


## fake SWVXX as Cash (if any)
data[data$Holding == 'SWVXX',]$Holding <- 'Cash'

## yahoo uses "-" instead of "." in symbol names so convert
data$Holding <- gsub("\\.", "-", data$Holding)

## strip df to only what is needed to identify unique accounts
data_accounts <- select(data, c('Owner', 'Account_Type', 'Holding', 'Shares'))

## identify securities
security <- unique(data_accounts$Holding)

##-----------------------------------------------------------------------------
refreshprice <- TRUE
if (isTRUE(readprice)) {
    ## get current price info for each security
    allprice <- equityinfo(security, extract=c('Name', 'Previous Close', 'P/E Ratio'))
    ## replace NA closing value for Cash with 1.0
    row <- which(grepl('^NA$', row.names(allprice)))
    rownames(allprice)[rownames(allprice) == "NA"] <- "Cash"
    allprice[row,]$Name       <- 'Cash'
    ## set cash value to 1
    allprice[row,]$`P. Close` <- 1
    zoo::write.zoo(allprice, 'allprice.csv')
} else {
    ## read current price info from allprice.csv
    allprice <- xts::as.xts( readall('allprice.csv') )
}

    
refreshtwr <- TRUE
if (isTRUE(readprice)) {

    ## get twr for each security
    ## twr <- equityhistory(security, period='months')  # security[1:50] works, [1:60] does not
    alltwr <- NA
    for (i in 1:length(security)) {
        ## equityhistory works for list of 50 symbols but not 60
        ## maybe just do 1 at a time for now to keep simple
        cat('i = ', i, 'security =', security[i], '\n')
        if (security[i] == 'Cash') {
            ## cannot download price info
            Cash <- 0.001
            alltwr <- cbind(twr, Cash)
        } else {
            new <- equityhistory(security[i], period='months')  # 50 works, 60 does not
            alltwr <- cbind(alltwr, new$twr)     # xts cbind nicely lines up dates
        }
    }
    ## strip off 1st column
    alltwr$twr <- NULL 
    tail(alltwr)
    zoo::write.zoo(alltwr, 'alltwr.csv')

    ## get twr for the benchmark
    outbench <- equityhistory('SPY', period='months')
    zoo::write.zoo(outbench, 'benchtwr.csv')

} else {
    ## read historical twr info from file
    alltwr   <- xts::as.xts( readall('alltwr.csv') )
    benchtwr <- xts::as.xts( readall('benchtwr.csv') )
}

dlh need to check above, both write and read
    
##-----------------------------------------------------------------------------
## select a unique account or combine accounts for alpha/beta calculation
unique(data_accounts$Account_Type)
invest <- subset(data_accounts, data_accounts$Account_Type == "Investment")
ira    <- subset(data_accounts, data_accounts$Account_Type == "IRA - Traditional")
inher  <- subset(data_accounts, data_accounts$Account_Type == "IRA - Inherited Traditional")
roth   <- subset(data_accounts, data_accounts$Account_Type == "IRA - Roth")
work   <- subset(data_accounts, data_accounts$Account_Type == "403b")

## select on of the above
df <- ira

## combine duplicate entries if needed
df <- aggregate(df$Shares, by=list(df$Holding), FUN=sum)
names(df) <- c('Holding', 'Shares')

## convert data to vectors
asset   <- as.character(df$Holding)
shares  <- df$Shares

##-----------------------------------------------------------------------------
## get current prices for selected assets
## pulls our the right assets but not in asset (and shares) orer
pricedf <- allprice[row.names(allprice) %in% asset,]
## reorder price to match order in asset
pricedf <- test[match(asset, row.names(pricedf)),]
price <- pricedf$'P. Close'

## calculate value and weight of each asset
value      <- shares * price
totalvalue <- sum(value)
weight <- value / totalvalue


## strip out the dates need for alpha and beta
twr       <- xts::last(twr, n=12*duration)
benchmark <- as.numeric( xts::last(outbench$twr$SPY,  n=12*duration) )


## ##----------------------
## ## put twr and SPY into single dataframe then omit NAs
## combined <- data.frame(twr, benchmark)
## combined <- na.omit(combined)
## dates <- row.names(combined)
## range(dates)
## years <- ( as.numeric( as.Date(dates[length(dates)]) ) - as.numeric( as.Date(dates[1]) ) ) / 365.25
## years
## 
## ## split back into twr and benchmark
## lastcol   <- ncol(combined)
## twr       <- combined[, 1:(lastcol-1)]
## benchmark <- combined[, lastcol]
## ##----------------------

## calculate alpha and beta for each asset
beta  <- NA
alpha <- NA
plotspace(2,2)
for (i in 1:length(asset)) {
    cat('i =', i, '; asset =', asset[i], '\n')
    twr_asset <- as.numeric(twr[,i])

    ## eliminate NAs for this asset / benchmark pair
    dftemp <- na.omit( data.frame(twr_asset, benchmark) )
    twr_asset <- dftemp[,1]
    benchmark <- dftemp[,2]

    ## determine alpha and beta for asset i
    out <- alpha_beta(twr_asset, benchmark, 
                      plot = TRUE, ylabel=asset[i],
                      range = range(twr, benchmark, na.rm = TRUE))
    alpha[i] <- out$alpha
    beta[i]  <- out$beta
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
stats <- rbind(stats, portfolio)
print(stats)

## plot portfolio
out <- plotfit(stats$beta, stats$alpha, stats$asset, nofit=TRUE)
xx <- stats[nrow(stats),]$beta
yy <- stats[nrow(stats),]$alpha
color <- as.character(out$legend[nrow(out$legend),]$color)
points(xx, yy, pch=16, col=color)

## ## plot interactive
## if (os == 'windows') {
##     ## following uses plotly which does not work on Chromebook
##     plot_interactive(stats, 'beta', 'alpha')
## }

library(shiny)
shinyplot(as.data.frame(stats), 'beta', 'alpha')
