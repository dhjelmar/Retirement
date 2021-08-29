## https://israeldi.github.io/bookdown/_book/monte-carlo-simulation-of-stock-portfolio-in-r-matlab-and-python.html

source('/home/dlhjel/GitHub_repos/R-setup/setup.r')


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
## Set number of days for the simulation
sim_time = 36
## Set simulation start date to start with current month since my returns are monthly
sim_start <- as.Date(format(Sys.Date(), "%Y-%m-01"))
## uncomment following to enter start date (use 1st of month if return and spending data are eom)
## sim_start <- as.Date('2022-01-01', %Y-%m-%d)
## Create sequence of dates at ends of months for simulation 
## (+1 on sim_time is so start with initial value)
Date <- seq(as.Date(sim_start), length=sim_time+1, by="1 month") - 1

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

## convert date field to date format
return_in$Date <- as.Date(return_in$Date, "%m/%d/%y")
spending_in$Date <- as.Date(spending_in$Date, "%m/%d/%y")
saving_in$Date   <- as.Date(saving_in$Date, "%m/%d/%y")
naccts <- ncol(return_in) - 1

## convert return columns as matrix for efficiency later
returnm <- as.matrix(return_in[2:ncol(return_in)])


## following commented out because reading rather than calculating returns
## # This function returns the first differences of a t x q df of data
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
coVarMat <- cov(returnm)
print(coVarMat)

## Lower Triangular Matrix from Choleski Factorization, L where L * t(L) = coVarMat
## check with as.matrix(L) %*% as.matrix(t(L)) = coVarMat
## needed for R_i = mean_i + L_ij * Z_ji
L = t( chol(coVarMat) )
print(L)


##-----------------------------------------------------------------------------
## modify saving and spending dataframes to have 1st column have all dates in 'Date'
## then need to modify mc loop to use new dataframes
endcol <- ncol(saving_in)
savingdf <- as_tibble(data.frame(matrix(0,    # Create data frame of zeros
                        nrow = length(Date),
                        ncol = endcol)))
names(savingdf) <- names(saving_in)
savingdf$Date <- Date
spendingdf <- savingdf # copy blank saving dataframe to spending dataframe
## add each user specified entry to savingdf
for (i in 1:nrow(saving_in)) {
  irow <- birk::which.closest(Date, saving_in$Date[i])
  savingdf[irow, 2:endcol] <- saving_in[i, 2:endcol]
  }
## add each user specified entry to savingdf
for (i in 1:nrow(spending_in)) {
  irow <- birk::which.closest(Date, spending_in$Date[i])
  spendingdf[irow, 2:endcol] <- spending_in[i, 2:endcol]
}

##-----------------------------------------------------------------------------
## START MONTE CARLO SIMULATION

## SPEEDUP ATTEMPT
## convert dataframes to matrices
spendingm <- as.matrix(spendingdf[2:naccts])
savingm   <- as.matrix(savingdf[2:naccts])

## initialize variables
twr_m <- matrix(0, sim_time, mc_rep) # row for each sim date; col for each mc sim
## totalvalue <- as_tibble(data.frame(matrix(0, sim_time+1, mc_rep)))
totalvaluem <- matrix(0, sim_time+1, mc_rep)
totalvaluem[1,] <- tvalue0
valuem <- returnm
valuem[,] <- 0
valuem[1,] <- as.matrix(value0)
    
## Extend means vector to a matrix
## one row for each account (or investment column) repeated in columns for each simulation
means_matrix = matrix(rep(means, sim_time), nrow = ncol(returnm))

## set seed if want to repeat exactly
set.seed(200)
for (i in 1:mc_rep) {
    ## do following for each monte carlo simulation

    cat('simulation', i, '\n')
    
    ## obtain random z values for each account (rows) for each date increment (columns)
    Z <- matrix( rnorm( ncol(returnm) * sim_time ), ncol = sim_time)

    ## simulate returns for each increment forward in time (assumed same as whatever data was)
    sim_return <- means_matrix + L %*% Z
    ## to view as a dataframe
    ## dfsim <- as_tibble(as.data.frame(t(sim_return)))

    ## Calculate vector of portfolio returns
    twr_i <- cumprod( weights %*% sim_return + 1 ) # sim_time entries
    
    ## Add it to the monte-carlo matrix
    twr_m[,i] <- twr_i;
    
    for (j in 1:sim_time) {
        ## for each time increment
        
        ## reduce value to reflect spending at start of time increment
        ##                        invest,    ira,   roth
        ## spent <- value[j,] + c(- 1000,      0,     0)
        ## spent <- value[j,] + monthly - spendingdf[j+1, 2:ncol(spendingdf)]
        ## spent <- monthly_spending + spendingdf[j+1, 2:ncol(spendingdf)]
        spent <- monthly_spending + spendingm[j+1,]
      
        ## update value from reduced starting value and simulated return
        ## growth <- spent + t(sim_return)[j,] * spent
        growth <- t(sim_return)[j,] * (value[j,] - spent)
        
        ## increase value to reflect additions at end of time increment
        ##                           invest,    ira,    roth
        ## value[j+1,] <- growth + c(- 1000,      0,     0)
        ## value[j+1,] <- growth + savingdf[j+1, 2:ncol(spendingdf)]
        added <- monthly_saving + savingm[j+1,]
        
        ## total value for simulation i
        value[j+1,] <- value[j,] - spent + growth + added
        totalvaluem[j+1, i] <- sum(value[j+1,])
        
        ## recalculate weights after adjustments
        weights <- as.numeric(value[j+1,] / sum(value[j+1,]))
    }
}
## put results into dataframe
twr_df <- as_tibble(as.data.frame(twr_m))
## add row for starting value
ones <- rep(1, ncol(twr_df))
twr_df <- rbind(ones, twr_df)


##-----------------------------------------------------------------------------
## DISPLAY RESULTS

## plot results
plotspace(2,1)

## PLOT TWR
## --------
## first establish plot area
ylim <- range(twr_df)
plot(Date, twr_df$V1, type='n',
     ylab='Simulation Returns',
     ylim=ylim)
for (i in 2:ncol(twr_df)) {
    lines(Date, t(twr_df[i]), type='l')
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
df <- twr_df
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
ylim <- range(totalvaluem)
plot(Date, t(totalvaluem[1]), type='n',
     ylab='Simulation Value',
     ylim=ylim)
for (i in 2:ncol(totalvaluem)) {
    lines(Date, t(totalvaluem[i]), type='l')
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
df <- totalvaluem
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
cum_final <- as.numeric( twr_df[nrow(twr_df),] )
cum_final_stats <- data.frame(mean   = mean(cum_final),
                              median = median(cum_final),
                              sd     = sd(cum_final))
print(cum_final_stats)

final <- cbind(savingdf, spendingdf[2:ncol(spendingdf)], ci(twr_df, 0.001), ci(totalvaluem, 0.001))
cat('                   Saving            Spending      TWR (99.9% LB CI)   Value (99.9% LB CI)\n',
    '             ------------------ ------------------ ------------------  -------------------\n')
print(final)
ci(twr_df, 0.999)
