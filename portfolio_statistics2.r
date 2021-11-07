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
data <- data[ (data$Account_Type != '401k (Flour)' &
               data$Account_Type != 'Bank' &
               data$Account_Type != 'Credit cards' &
               data$Account_Type != 'Primary home' &
               data$Account_Type != 'Vacation home'),]
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
if (isTRUE(refreshprice)) {
    ## get current price info for each security
    allprice <- equityinfo(security, extract=c('Name', 'Previous Close', 'P/E Ratio'))
    names(allprice) <- c('date', 'name', 'close', 'pe_ratio')
    ## replace NA closing value for Cash with 1.0
    narow <- which(grepl('^NA$', row.names(allprice)))
    rownames(allprice)[rownames(allprice) == "NA"] <- "Cash"
    allprice[narow,]$name       <- 'Cash'
    ## set cash value to 1
    allprice[narow,]$close <- 1
    write.csv(allprice, 'out_allprice.csv')

} else {
    ## read current price info from allprice.csv
    allprice <- read.csv('out_allprice.csv')
    rownames(allprice) <- allprice$X
    allprice$X <- NULL
}

    
refreshtwr <- TRUE
if (isTRUE(refreshtwr)) {

    ## get twr for each security
    ## twr <- equityhistory(security, period='months')  # security[1:50] works, [1:60] does not
    alltwr <- NA
    for (i in 1:length(security)) {
        ## equityhistory works for list of 50 symbols but not 60
        ## maybe just do 1 at a time for now to keep simple
        cat('i = ', i, 'security =', security[i], '\n')
        if (security[i] == 'Cash') {
            ## cannot download price info  with tiny variation so statistics work later
            Cash <- rnorm(nrow(alltwr), mean=0, sd=0.00001)
            alltwr <- cbind(alltwr, Cash)
        } else {
            new <- equityhistory(security[i], period='months')  # 50 works, 60 does not
            alltwr <- cbind(alltwr, new$twr)     # xts cbind nicely lines up dates
        }
    }
    ## strip off 1st column
    alltwr$alltwr <- NULL 
    tail(alltwr)
    zoo::write.zoo(alltwr, 'out_alltwr.csv', sep=',')

    ## get twr for the benchmark
    outbench <- equityhistory('SPY', period='months')$twr
    zoo::write.zoo(outbench, 'out_benchtwr.csv', sep=',')

} else {
    ## read historical twr info from file
    
    alltwr <- readall('out_alltwr.csv')
    rownames(alltwr) <- alltwr$Index
    alltwr$Index     <- NULL
    alltwr <- xts::as.xts(alltwr)
    
    benchtwr <- readall('out_benchtwr.csv')
    rownames(benchtwr) <- benchtwr$Index
    benchtwr$Index     <- NULL
    benchtwr <- xts::as.xts(benchtwr)
    
}


##-----------------------------------------------------------------------------
## select a unique account or combine accounts for alpha/beta calculation
unique(data_accounts$Account_Type)
## split account info by Acount_Type into a list of dataframes
account <- split(data_accounts, data_accounts$Account_Type)
names(account)
## select one to work with
i <- 1
dfname <- names(account)[i]
print(dfname)
df <- account[[1]]

## ## alternately could have used subset to pull out a single account or combine accounts
## invest <- subset(data_accounts, data_accounts$Account_Type == "Investment")
## ira    <- subset(data_accounts, data_accounts$Account_Type == "IRA - Traditional")
## dfname <- 'ira'
## df     <- ira

## combine duplicate entries if needed and drop columns except for Holding and Shares
df <- aggregate(df$Shares, by=list(df$Holding), FUN=sum)
names(df) <- c('Holding', 'Shares')

## convert data to vectors
asset   <- as.character(df$Holding)
shares  <- df$Shares

##-----------------------------------------------------------------------------
## get current prices for selected assets
## pulls our the right assets but not in asset (and shares) order
pricedf <- allprice[row.names(allprice) %in% asset,]
## reorder price to match order in asset
pricedf <- pricedf[match(asset, row.names(pricedf)),]
price <- pricedf$'close'

## calculate value and weight of each asset
value      <- shares * price
totalvalue <- sum(value)
weight <- value / totalvalue

## strip out the dates needed for alpha and beta
## combine twr and benchmarks to line up dates
both <- cbind(alltwr, benchtwr)
## select the number of dates requested based on input duration
both <- xts::last(both, n=12*duration)
twr       <- both[, 1:ncol(twr)]
benchmark <- both[,  (ncol(twr)+1):ncol(both)]
benchmark <- as.numeric( benchmark )

## twr       <- xts::last(alltwr,        n=12*duration)                # keep as xts for now
## benchmark <- as.numeric( xts::last(benchtwr$SPY,  n=12*duration) )  # converted to vector

## calculate alpha and beta for each asset
beta  <- NA
alpha <- NA
twri  <- NA
for (i in 1:length(asset)) {
    cat('i =', i, '; asset =', asset[i], '\n')
    twr_asset <- as.numeric(twr[,i])

    ## eliminate NAs for this asset / benchmark pair
    dftemp <- na.omit( data.frame(twr_asset, benchmark) )
    twr_asset   <- dftemp[,1]
    bench_asset <- dftemp[,2]

    ## determine alpha and beta for asset i
    plotspace(2,2)
    out <- alpha_beta(twr_asset, bench_asset, 
                      plot = TRUE, ylabel=asset[i],
                      range = range(twr, bench_asset, na.rm = TRUE))
    alpha[i] <- out$alpha
    beta[i]  <- out$beta

    ## determine twr for asset i
    twri[i]  <- prod(twr_asset+1)-1

    ## plot histogram of alpha and beta for asset 1
    hist_nwj(twr_asset, type='nj')
    qqplot_nwj(twr_asset, type='n')
    qqplot_nwj(twr_asset, type='j')
    
}
## filter the dataframe with all assets to only include the assets being evaluated
assetname <- allprice[rownames(allprice) %in% asset,]
## reorder the list of assets to match the requested order
assetname <- assetname[match(asset, row.names(assetname)),]
## extract the asset name
assetname <- assetname$name

stats <- data.frame(asset,
                    name = assetname,
                    shares = as.numeric(shares), 
                    value=as.numeric(value), 
                    twr  = twri,
                    beta, 
                    alpha)
## sort from low to high twr
stats <- stats[order(stats$twr),]

## calculate portfolio beta
beta_portfolio  <- sum( weight * beta  )
alpha_portfolio <- sum( weight * alpha )
twr_portfolio   <- sum( weight * twri  )
portfolio <- data.frame(asset  = dfname, 
                        name   = 'portfolio',
                        shares = NA, 
                        value  = totalvalue, 
                        twr    = twr_portfolio,
                        beta   = beta_portfolio,
                        alpha  = alpha_portfolio)
statsall <- rbind(stats, portfolio)
print(statsall)

## plot portfolio
plotspace(1,2)
out <- plotfit(stats$beta, stats$alpha, stats$asset, nofit=TRUE)
## xx <- stats[nrow(stats),]$beta
## yy <- stats[nrow(stats),]$alpha
## color <- as.character(out$legend[nrow(out$legend),]$color)
## points(xx, yy, pch=16, col=color)
out <- plotfit(stats$twr, stats$alpha, stats$asset, nofit=TRUE)

## any correlation between alpha, beta, and twr?
abtwr <- select(stats, alpha, beta, twr)
pairsdf(abtwr)



## ## plot interactive
## if (os == 'windows') {
##     ## following uses plotly which does not work on Chromebook
##     plot_interactive(stats, 'beta', 'alpha')
## }

library(shiny)
shinyplot(as.data.frame(stats), 'beta', 'alpha')
