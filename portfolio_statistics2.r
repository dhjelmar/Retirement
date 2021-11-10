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
duration = 1

if (os == 'unix') {
    file <- 'all.xlsx'
    data <- readall(file, sheet="Assets + Liabilities")

    ## dlh in xlsx file, change "Holding" to "Symbol"
    ##                          "Shares"  to "Quantity"
    
} else {
    file <- "F:\\Documents\\01_Dave's Stuff\\Finances\\allocation.xlsx"
    data <- readall(file, sheet='all assets', header.row.start=2, data.row.start=4)
}

## delete non-security info (dlh remove this once clean xlsx)
data <- data[ (data$Account_Type != '401k (Flour)' &
               data$Account_Type != 'Bank' &
               data$Account_Type != 'Credit cards' &
               data$Account_Type != 'Primary home' &
               data$Account_Type != 'Vacation home'),]
data <- data[(data$Symbol      != 'SCGE1' &
               data$Symbol      != 'SCGI1' &
               data$Symbol      != 'SCGL1' &
               data$Symbol      != 'SCGN1' &
               data$Symbol      != 'SCGS1' &
               data$Symbol      != 'SCII1'),]


## fake SWVXX as Cash (if any)
data[data$Symbol == 'SWVXX',]$Symbol <- 'Cash'

## yahoo uses "-" instead of "." in symbol names so convert
data$Symbol <- gsub("\\.", "-", data$Symbol)

## strip df to only what is needed to identify unique accounts
data_accounts <- select(data, c('Owner', 'Account_Type', 'Symbol', 'Quantity'))

## identify securities
security <- unique(data_accounts$Symbol)

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

    
refreshtwr <- FALSE
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
    benchname <- 'SPY'
    benchtwr <- equityhistory(benchname, period='months')$twr
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

## combine duplicate entries if needed and drop columns except for Symbol and Quantity
df <- aggregate(df$Quantity, by=list(df$Symbol), FUN=sum)
names(df) <- c('Symbol', 'Quantity')

## convert data to vectors
asset   <- as.character(df$Symbol)
shares  <- df$Quantity

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

## get twr for each requested assset
twr <- alltwr[, names(alltwr) %in% asset]
## reorder twr to match order in asset
twr <- twr[, match(asset, names(twr))]

## strip out the dates needed for alpha and beta
## combine twr and benchmarks to line up dates
both <- cbind(twr, benchtwr)
## select the number of dates requested based on input duration
both <- xts::last(both, n=12*duration)
twr       <- both[, 1:ncol(twr)]
benchmark <- both[,  (ncol(twr)+1):ncol(both)]
benchmark <- as.numeric( benchmark )

## filter the dataframe with all assets to only include the assets being evaluated
assetname <- allprice[rownames(allprice) %in% asset,]
## reorder the list of assets to match the requested order
assetname <- assetname[match(asset, row.names(assetname)),]
## extract the asset name
assetname <- assetname$name

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
                      plot = TRUE, 
                      xlabel = paste('Incremental TWR for', benchname, sep=' '),
                      ylabel = paste('Incremental TWR for', asset[i], sep=' '),
                      range  = range(twr, benchmark, na.rm = TRUE),
                      main   = assetname[i])
    alpha[i] <- out$alpha
    beta[i]  <- out$beta

    ## determine twr for asset i
    twri[i]  <- prod(twr_asset+1)-1

    ## plot histogram of alpha and beta for asset 1
    out <- hist_nwj(twr_asset, type='nj', upperbound=FALSE,
                    main="Histogram of Incremental Returns")
    out <- qqplot_nwj(twr_asset, type='n')
    out <- qqplot_nwj(twr_asset, type='j')
    
}
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
stats <- rbind(stats, portfolio)
print(stats)

## plot portfolio
plotspace(1,2)
out <- plotfit(stats$alpha, stats$beta, stats$asset, nofit=TRUE)
## xx <- stats[nrow(stats),]$beta
## yy <- stats[nrow(stats),]$alpha
## color <- as.character(out$legend[nrow(out$legend),]$color)
## points(xx, yy, pch=16, col=color)
out <- plotfit(stats$alpha, stats$twr, stats$asset, nofit=TRUE)

## any correlation between alpha, beta, and twr?
abtwr <- select(stats, twr, alpha, beta)
pairsdf(abtwr)

## ## plot interactive
## if (os == 'windows') {
##     ## following uses plotly which does not work on Chromebook
##     plot_interactive(stats, 'beta', 'alpha')
## }

library(shiny)
shinyplot(as.data.frame(stats), 'beta', 'alpha')
