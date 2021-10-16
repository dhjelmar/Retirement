f## https://israeldi.github.io/bookdown/_book/monte-carlo-simulation-of-stock-portfolio-in-r-matlab-and-python.html

source('/home/dlhjel/GitHub_repos/R-setup/setup.r')
path <- '/home/dlhjel/GitHub_repos/Retirement/'
setwd(path)
r_files <- list.files(paste(path,'modules',sep=""), pattern="*.[rR]$", full.names=TRUE)
for (f in r_files) {
  ## cat("f =",f,"\n")
  source(f)
}


##-----------------------------------------------------------------------------
## SET PARAMETERS FOR MONTE CARLO SIMULATIONS
## Set number of Monte Carlo Simulations
mc_rep = 10
## Set simulation start date to start with current month since my returns are monthly
sim_start <- as.Date(format(Sys.Date(), "%Y-%m-01"))
sim_end   <- as.Date('2021-12-31')


##-----------------------------------------------------------------------------
## OBTAIN BENCHMARK HISTORICAL DATA
## category       ETF  description
## -------------  ---  ---------------
## USL            SPY  S&P 500
## USS            IWM  Russell 2000
## International  EFA  MSCI EAFE (TRN)
## Fixed          AGG  Bloomberg US Aggregate Bond
## Cash           SHV FTSE 3-month treasury bill

period <- 'days'
## periods per year
if (period == 'years') {
    nperiod <- 1
} else if (period == 'months') {
    nperiod <- 12
} else if (period == 'weeks') {
    nperiod <- 52
} else {
    ## days
    ## number of periods will change a bit each year
    ## 365.25 (days on average per year) * 5/7 (proportion work days per week)
    ## - 6 (weekday holidays) - 3*5/7 (fixed date holidays) = 252.75 ≈ 253
    nperiod <- 253
}

out <- equityget(c('SPY', 'IWM', 'EFA', 'AGG', 'SHV'), from='1995-01-01',
                 period=period)
benchclose  <- out$close
benchtwr    <- out$twr
colnames(benchclose) <- c('US_L', 'US_S', 'Inter', 'Fixed', 'Cash')
colnames(benchtwr)  <- c('US_L', 'US_S', 'Inter', 'Fixed', 'Cash')
## plot closing prices and TWR
plotspace(1,2)
plotxts(benchclose)
## plotzoo(benchclose)
plotxts(benchtwr)

## only keep twr for dates where all are defined
benchtwr <- na.omit(benchtwr)


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
monthly_change <-  monthly_saving - monthly_spending

## calculate changes per period
period_change  <- monthly_change * 12 / nperiod


## set specific date spending and saving (specify at end of a period)
saving <- '
    Date    invest    ira   roth
2/28/22          0  20000       0     
3/30/22         0      0   50000 
'
saving <- readall(saving)
saving_in   <- as_tibble(saving)
saving_in$Date   <- as.Date(saving_in$Date, "%m/%d/%y")

spending <- '
    Date    invest    ira   roth
1/31/22     1000        0      0
4/30/22        0     5000      0
'
spending <- readall(spending)
spending_in <- as_tibble(spending)
spending_in$Date <- as.Date(spending_in$Date, "%m/%d/%y")

## convert to XTS
saving   <- xts::as.xts(zoo::read.zoo(saving,   index.column = 1, format = "%m/%d/%Y" ))
spending <- xts::as.xts(zoo::read.zoo(spending, index.column = 1, format = "%m/%d/%Y" ))



##-----------------------------------------------------------------------------
## determine number of timesteps and create date sequence
if (period == 'years') {
    ntimestep <- as.numeric(format(sim_end, "%Y")) - as.numeric(format(sim_start,"%Y"))
    ## Create sequence of dates at ends of periods for simulation 
    ## (+1 on ntimestep is so start with initial value)
    Date      <- seq(as.Date(sim_start), length=ntimestep+1, by=period) - 1
} else if (period == 'months') {
    ntimestep <- lubridate::interval(sim_start, sim_end) %/% months(1) + 1
    Date      <- seq(as.Date(sim_start), length=ntimestep+1, by=period) - 1
} else if (period == 'weeks') {
    ntimestep <- ceiling( (sim_end - sim_start) / 7 )  # rounds up
    Date      <- seq(as.Date(sim_start), length=ntimestep+1, by=period) - 1
} else {
    ## period = 'days'
    ## install.packages('bizdays')
    holidays <- timeDate::holidayNYSE(year = c(2021:2051))
    bizdays::create.calendar("USA", holiday =holidays, weekdays=c("saturday", "sunday"))
    Date <- bizdays::bizseq(sim_start, sim_end, "USA")
}
## Number of timesteps for the simulation
ntimestep = length(Date)

## split off 1st date since mc will only iterate on future dates
date0    <- Date[1]
datesim  <- Date[2:length(Date)]


##-----------------------------------------------------------------------------
## Define starting value and weights for each asset and total value
value0 <- data.frame(invest = 10000,
                     ira    = 20000,
                     roth   = 30000)
tvalue0 <- sum(value0)
weights <- c(value0[[1]]/tvalue0,
             value0[[2]]/tvalue0,
             value0[[3]]/tvalue0)
print(weights)

## Define asset allocation for each account
allocation <- '
account US_L US_S Inter Fixed Cash
invest    50   10     0    30   10
ira       40   30     5    20    5
roth      50   30    10    10    0
'
allocation <- readall(allocation)
print(allocation)


##-----------------------------------------------------------------------------
## READ IN DATA FOR EACH ASSET

## ##----------------------
## ## OLD
## return_in   <- as_tibble(readall(return))
## naccts      <- ncol(return_in) - 1
## 
## ## convert date field to date format
## return_in$Date   <- as.Date(return_in$Date, "%m/%d/%y")
## 
## ## convert return columns as matrix for efficiency later
## returnm <- as.matrix(return_in[2:ncol(return_in)])
## ## OLD
## ##----------------------

returnm     <- benchtwr

## calculate mean return for each asset
means <- colMeans(returnm)

## Get the Variance Covariance Matrix of asset returns
plotspace(1,1)
plot.new()
pairsdf(as.matrix(returnm))
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
