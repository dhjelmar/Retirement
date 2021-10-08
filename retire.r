## https://israeldi.github.io/bookdown/_book/monte-carlo-simulation-of-stock-portfolio-in-r-matlab-and-python.html

source('/home/dlhjel/GitHub_repos/R-setup/setup.r')
path <- '/home/dlhjel/GitHub_repos/Retirement/'
setwd(path)
r_files <- list.files(paste(path,'modules',sep=""), pattern="*.[rR]$", full.names=TRUE)
for (f in r_files) {
  ## cat("f =",f,"\n")
  source(f)
}

##-----------------------------------------------------------------------------
## OBTAIN BENCHMARK HISTORICAL DATA
## category       ETF  description
## -------------  ---  ---------------
## USL            SPY  S&P 500
## USS            IWM  Russell 2000
## International  EFA  MSCI EAFE (TRN)
## Fixed          AGG  Bloomberg US Aggregate Bond
## Cash           SHV FTSE 3-month treasury bill

out <- equityget(c('SPY', 'IWM', 'EFA', 'AGG', 'SHV'), from='1995-01-01')
close  <- out$close
twr    <- out$twr
colnames(close) <- c('US_L', 'US_S', 'Inter', 'Fixed', 'Cash')
colnames(twr)  <- c('US_L', 'US_S', 'Inter', 'Fixed', 'Cash')
## plot
plotspace(1,2)
plotxts(close)
plotxts(twr)



benchmarkdf <- as.data.frame(benchmarkm)
pairsdf(benchmarkdf)
pairsdf(na.omit(benchmarkdf))
benchmarkdf$date <- as.Date( rownames(benchmarkdf) )
plotdfall(benchmarkdf, 'date', size=0.01, type='b')

closedf <- as.data.frame(closem)
closedf$date <- as.Date( rownames(closedf) )
plotdfall(closedf, 'date', size=0.01, type='b')

## convert above into TWR
nrows <- nrow(benchmark_xts)
returnp1 <- benchmark_xts[2:nrows] / benchmark_xts[1:(nrows-1)]
return   <- returnp1 - 1

head(returnp1)
head(return * 100)


a <- head(benchmark_xts[2:nrows]) - 28
b <- head(benchmark_xts[1:(nrows-1)]) - 28
a/b

dlh not sure why above does not work




##-----------------------------------------------------------------------------
## DATA FOR EACH ASSET

## Determine mean for each asset and covariance matrix
return <- '
    Date    invest    ira   roth
1/31/17       0.01   0.02   0.03
2/28/17       0.02   0.03   0.05
3/31/17       0.05   0.04   0.30
4/30/17       0.03   0.05   0.02
5/31/17       0.05   0.04   0.02
6/30/17       0.07   0.08   0.01
7/31/17       0.08   0.07   -0.02
8/31/17       0.05   0.07   0.02
9/30/17       0.08   0.10   0.03
10/31/17      0.09   0.10   0.05
11/30/17      0.10   0.09   0.02
12/31/17      0.10   0.09   0.03
1/31/17       0.06   0.08   0.05
2/28/17       0.03   0.04   0.06
3/31/17       0.01   0.05   0.06
'

## set monthly changes to accounts
monthly_spending <- c( 1000, 
                       0, 
                       0)
monthly_saving   <- c( 500, 
                       0, 
                       0)

## set specific date spending (specify at end of month)
spending <- '
    Date    invest    ira   roth
1/31/22     1000        0      0
4/30/22        0     5000      0
'

saving <- '
    Date    invest    ira   roth
2/28/22          0  20000       0     
3/30/22         0      0   50000 
'


##-----------------------------------------------------------------------------
## SET PARAMETERS FOR MONTE CARLO SIMULATIONS

## Set number of Monte Carlo Simulations
mc_rep = 10
## Set number of timesteps for the simulation
ntimestep = 36
## Set simulation start date to start with current month since my returns are monthly
sim_start <- as.Date(format(Sys.Date(), "%Y-%m-01"))
## uncomment following to enter start date (use 1st of month if return and spending data are eom)
## sim_start <- as.Date('2022-01-01', %Y-%m-%d)
## Create sequence of dates at ends of months for simulation 
## (+1 on ntimestep is so start with initial value)
Date     <- seq(as.Date(sim_start), length=ntimestep+1, by="1 month") - 1
## split off 1st date since mc will only iterate on future dates
date0    <- Date[1]
datesim  <- Date[2:length(Date)]

## Define starting value and weights for each asset and total value
value0 <- data.frame(invest = 10000,
                     ira    = 20000,
                     roth   = 30000)
tvalue0 <- sum(value0)
weights <- c(value0[[1]]/tvalue0,
             value0[[2]]/tvalue0,
             value0[[3]]/tvalue0)

print(weights)


##-----------------------------------------------------------------------------
## READ IN DATA FOR EACH ASSET

return_in   <- as_tibble(readall(return))
spending_in <- as_tibble(readall(spending))
saving_in   <- as_tibble(readall(saving))
naccts      <- ncol(return_in) - 1

## convert date field to date format
return_in$Date   <- as.Date(return_in$Date, "%m/%d/%y")
spending_in$Date <- as.Date(spending_in$Date, "%m/%d/%y")
saving_in$Date   <- as.Date(saving_in$Date, "%m/%d/%y")

## convert return columns as matrix for efficiency later
returnm <- as.matrix(return_in[2:ncol(return_in)])

## following commented out because reading rather than calculating returns
## returns = function(df){
##   rows  <- nrow(df)
##   return <- df[2:rows, ] / df[1:rows-1, ] - 1
## }
## 
## # Get the asset returns
## return <- returns(price)

## calculate mean return for each asset
means <- colMeans(returnm)

## Get the Variance Covariance Matrix of asset returns
pairsdf(returnm)
covarm <- cov(returnm)
print(covarm)

## Lower Triangular Matrix from Choleski Factorization, L where L * t(L) = covarm
## check with as.matrix(L) %*% as.matrix(t(L)) = covarm
## needed for R_i = mean_i + L_ij * Z_ji
L = t( chol(covarm) )
print(L)


##-----------------------------------------------------------------------------
## modify saving and spending dataframes to have 1st column have all dates in 'datesim'
## then need to modify mc loop to use new dataframes
endcol <- ncol(saving_in)
saving <- as_tibble(data.frame(matrix(0,    # Create data frame of zeros
                        nrow = length(datesim),
                        ncol = endcol)))
names(saving) <- names(saving_in)
saving$Date <- datesim
spending <- saving # copy blank saving dataframe to spending dataframe
## add each user specified entry to saving
for (i in 1:nrow(saving_in)) {
  irow <- birk::which.closest(datesim, saving_in$Date[i])
  saving[irow, 2:endcol] <- saving_in[i, 2:endcol]
}
## add each user specified entry to saving
for (i in 1:nrow(spending_in)) {
  irow <- birk::which.closest(datesim, spending_in$Date[i])
  spending[irow, 2:endcol] <- spending_in[i, 2:endcol]
}
## add monthly saving and spending
for (i in 1:nrow(saving)) {
    saving[i, 2:endcol]   <- saving[i, 2:endcol]   + monthly_saving
    spending[i, 2:endcol] <- spending[i, 2:endcol] + monthly_spending
}

##-----------------------------------------------------------------------------
## START MONTE CARLO SIMULATION

## SPEEDUP ATTEMPT
## convert dataframes to matrices
savingm   <- as.matrix(saving[2:(naccts+1)])
spendingm <- as.matrix(spending[2:(naccts+1)])

## initialize variables
## twr and totalvalue matrices
## row for each timestep
## column for each mc sim
twrm        <- matrix(0, ntimestep, mc_rep)
totalvaluem <- twrm
## same as above for value but with 2nd dimension for each account 
valuem     <- array(0, dim=c(ntimestep, naccts, mc_rep))

## Extend means vector to a matrix
## one row for each account (or investment column) repeated in columns for each timestep
meansm = matrix(rep(means, ntimestep), nrow = ncol(returnm))

## set seed if want to repeat exactly
set.seed(200)
for (i in 1:mc_rep) {
    ## do following for each monte carlo simulation

    cat('simulation', i, '\n')

    ## start with initial values for each account
    valueold   <- value0
    
    ## obtain random z values for each account (rows) for each date increment (columns)
    Z <- matrix( rnorm( naccts * ntimestep ), ncol = ntimestep)

    ## simulate returns for each increment forward in time (assumed same as whatever data was)
    sim_return <- meansm + L %*% Z
    ## to view as a dataframe
    ## dfsim <- as_tibble(as.data.frame(t(sim_return)))

    ## Calculate vector of portfolio returns
    twr_i <- cumprod( weights %*% sim_return + 1 ) -1 # ntimestep entries
    
    ## Add it to the monte-carlo matrix
    twrm[,i] <- twr_i;
    
    for (j in 1:ntimestep) {
        ## for each time increment
        
        ## reduce value to reflect spending at start of time increment
        spent <- spendingm[j,]
      
        ## update value from reduced starting value and simulated return
        ## growth <- spent + t(sim_return)[j,] * spent
        growth <- t(sim_return)[j,] * (valueold - spent)
        
        ## increase value to reflect additions at end of time increment
        added <- savingm[j,]
        
        ## value for simulation i
        valuem[j,,i] <- as.numeric(valueold - spent + growth + added)
        ## value for each account
        valueold     <- valuem[j,,i]
        ## total value for all accounts combined
        totalvaluem[j,i] <- sum(valueold)
        
        ## recalculate weights after adjustments
        weights <- as.numeric(valueold / sum(valueold))
    }
}

##-----------------------------------------------------------------------------
## GATHER RESULTS

## add row for starting 0s for saving and spending dfs
zeros <- rep(0, naccts)
zeros <- data.frame(Date[1], t(zeros))
names(zeros) <- names(saving)
saving   <- as_tibble(rbind(zeros, saving))
spending <- as_tibble(rbind(zeros, spending))

## put twrm results into dataframe
twr <- as.data.frame(twrm)
## add row for starting value
ones <- rep(0, ncol(twr))
twr <- rbind(ones, twr)
## ## add date
## twr <- as_tibble(cbind(Date=Date, twr))

## put total value results into dataframe
totalvalue <- as.data.frame(totalvaluem)
totalvalue <- rbind(sum(value0), totalvalue)
## totalvalue <- as_tibble(cbind(Date=Date, totalvalue))

## valuem is size ntimestep x naccts x mc_rep
## e.g., valuem[1,,2] returns 1st timestep results for all account values for mc_rep=2
##       valuem[,,1]  returns all timestep results for all account values for mc_rep=1
##       valuem[,1,]  returns all timestep results for 1st account for all mc_reps



##-----------------------------------------------------------------------------
## DISPLAY RESULTS

## plot results
plotspace(2,1)

## PLOT TWR
## --------
## first establish plot area
ylim <- range(twr)
plot(Date, twr$V1, type='n',
     ylab='Simulation Returns',
     ylim=ylim)
for (i in 2:ncol(twr)) {
    lines(Date, t(twr[i]), type='l')
}

## Construct Confidential Intervals for returns
## first define function
ci <- function(df, conf) {
    ## calculate confidence limit for specified confidence level
    ## note specified conf = 1 - alpha
    ## i.e., if want alpha=0.05 to get 95% conf limit, specify 0.95
    apply(df, 1, function(x) quantile(x, conf))
}
## create dataframe of confidence intervals
df <- twr
cis <- as_tibble( data.frame(Date,
                             conf_99.9_upper_percent = ci(df, 0.999),
                             conf_99.0_upper_percent = ci(df, 0.99),
                             conf_95.0_upper_percent = ci(df, 0.95),
                             conf_50.0_percent       = ci(df, 0.5),
                             conf_95.0_lower_percent = ci(df, 0.05),
                             conf_99.0_lower_percent = ci(df, 0.01),
                             conf_99.9_lower_percent = ci(df, 0.001)) )

## plot confidence intervals on simulation
lines(cis$Date, cis$conf_99.9_upper_percent, lwd=4, lty=2, col='red')
lines(cis$Date, cis$conf_50.0_percent      , lwd=4,        col='red')
lines(cis$Date, cis$conf_99.9_lower_percent, lwd=4, lty=2, col='red')
legend('topleft', 
       legend=c('simulation', 'upper 99.99', 'mean', 'lower 99.99'),
       col=c('black', 'red', 'red', 'red'),
       lty=c(1,2,1,2))





## PLOT VALUE
## ----------
## first establish plot area
ylim <- range(totalvalue)
plot(Date, totalvalue$V1, type='n',
     ylab='Simulation Value',
     ylim=ylim)
for (i in 2:ncol(totalvalue)) {
    lines(Date, t(totalvalue[i]), type='l')
}

## Construct Confidential Intervals for returns
## first define function
ci <- function(df, conf) {
    ## calculate confidence limit for specified confidence level
    ## note specified conf = 1 - alpha
    ## i.e., if want alpha=0.05 to get 95% conf limit, specify 0.95
    apply(df, 1, function(x) quantile(x, conf))
}
## create dataframe of confidence intervals
df <- totalvalue
cis <- as_tibble( data.frame(Date,
                             conf_99.9_upper_percent = ci(df, 0.999),
                             conf_99.0_upper_percent = ci(df, 0.99),
                             conf_95.0_upper_percent = ci(df, 0.95),
                             conf_50.0_percent       = ci(df, 0.5),
                             conf_95.0_lower_percent = ci(df, 0.05),
                             conf_99.0_lower_percent = ci(df, 0.01),
                             conf_99.9_lower_percent = ci(df, 0.001)) )

## plot confidence intervals on simulation
lines(cis$Date, cis$conf_99.9_upper_percent, lwd=4, lty=2, col='red')
lines(cis$Date, cis$conf_50.0_percent      , lwd=4,        col='red')
lines(cis$Date, cis$conf_99.9_lower_percent, lwd=4, lty=2, col='red')
legend('topleft', 
       legend=c('simulation', 'upper 99.99', 'mean', 'lower 99.99'),
       col=c('black', 'red', 'red', 'red'),
       lty=c(1,2,1,2))


##-----------------------------------------------------------------------------
## final results at end of simulation
## Porfolio Returns statistics at end of simulation
cum_final <- as.numeric( twr[nrow(twr),] )
cum_final_stats <- data.frame(mean   = mean(cum_final),
                              median = median(cum_final),
                              sd     = sd(cum_final))
print(cum_final_stats)

final <- cbind(saving, spending[2:ncol(spending)], ci(twr, 0.001), ci(totalvalue, 0.001))
cat('                   Saving            Spending      TWR (99.9% LB CI)   Value (99.9% LB CI)\n',
    '             ------------------ ------------------ ------------------  -------------------\n')
print(final)
ci(twr, 0.999)


## ## create dataframe of mean and upper/lower ci for each account
## value <- data.frame(matrix(0,    # Create data frame of zeros
##                            nrow = length(datesim),
##                            ncol = mc_rep))
## for (i in 1:naccts) {
##     cat('account', i, '\n')
##     value <- valuem[,i,]
## }
