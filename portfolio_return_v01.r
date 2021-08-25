## https://israeldi.github.io/bookdown/_book/monte-carlo-simulation-of-stock-portfolio-in-r-matlab-and-python.html

source('/home/dlhjel/GitHub_repos/R-setup/setup.r')

##-----------------------------------------------------------------------------
## Determine mean for each asset and covariance matrix
data <- '
    Date           AAPL           GOOG           FB
11/15/17       166.5791        1020.91       177.95
11/16/17       168.5693        1032.50       179.59
11/17/17       167.6333        1019.09       179.00
11/20/17       167.4658        1018.38       178.74
11/21/17       170.5791        1034.49       181.86
11/22/17       172.3721        1035.96       180.87
11/24/17       172.3820        1040.61       182.78
11/27/17       171.5150        1054.21       183.03
11/28/17       170.5101        1047.41       182.42
11/29/17       166.9732        1021.66       175.13
'
history <- as_tibble(readall(data))
history$Date <- as.Date(history$Date, "%m/%d/%Y")
increment <- (max(history$Date) - min(history$Date)) / nrow(history)
# alternately, I could grab the most common increment
# increment <- mode(diff(history$Date))
price <- history[2:ncol(history)]

# This function returns the first differences of a t x q df of data
returns = function(df){
  rows  <- nrow(df)
  return <- df[2:rows, ] / df[1:rows-1, ] - 1
}

# Get the asset returns
return <- returns(price)

## calculate mean return for each asset
means = colMeans(return)

## Get the Variance Covariance Matrix of Stock Returns
pairs(return)
coVarMat = cov(return)
print(coVarMat)

## Lower Triangular Matrix from Choleski Factorization, L where L * t(L) = CoVarMat
## needed for R_i = mean_i + L_ij * Z_ji
L = t( chol(coVarMat) )
print(L)

##-----------------------------------------------------------------------------
## SET PARAMETERS FOR MONTE CARLO SIMULATIONS

# Set number of Monte Carlo Simulations
mc_rep = 1000
# Set number of days for the simulation
sim_days = 30
# Set simulation start date
sim_start <- Sys.Date()
# Calculate simulation end date
sim_end <- sim_start + increment * sim_days
# Set date vector for simulation (length should be sim_days + 1)
Date <- seq(sim_start, sim_end, increment)

# Suppose we invest our money evenly among all three assets 
# We use today's Price 11/14/2018 to find the number of shares each stock 
# that we buy
weights <- c(1/3, 1/3, 1/3)
print(weights)

##-----------------------------------------------------------------------------
## START MONTE CARLO SIMULATION

## initialize sim_return matrix 
## row for each simulation date
## column for each monte carlo simulation
cum_sim_m = matrix(0, sim_days, mc_rep)

## Extend means vector to a matrix
## one row for each account (or investment column) repeated in columns for each simulation
means_matrix = matrix(rep(means, sim_days), nrow = ncol(return))

## set seed if want to repeat exactly
set.seed(200)
for (i in 1:mc_rep) {
    ## do following for each monte carlo simulation

    ## obtain random z values for each account (rows) for each date increment (columns)
    Z <- matrix( rnorm( ncol(return) * sim_days ), ncol = sim_days)

    ## simulate returns for each increment forward in time (assumed same as whatever data was)
    sim_return <- means_matrix + L %*% Z
    ## to view as a dataframe
    ## dfsim <- as_tibble(as.data.frame(t(sim_return)))

    ## Calculate vector of portfolio returns
    cum_sim_i = cumprod( weights %*% sim_return + 1 )

    ## Add it to the monte-carlo matrix
    cum_sim_m[,i] = cum_sim_i;
}
# put results into dataframe
cum_sim_df <- as_tibble(as.data.frame(cum_sim_m))
# add row for starting value
ones <- rep(1, ncol(cum_sim_df))
cum_sim_df <- rbind(ones, cum_sim_df)


##-----------------------------------------------------------------------------
## DISPLAY RESULTS

# plot results
# first establish plot area
ylim <- range(cum_sim_df)
plot(Date, cum_sim_df$V1, type='n',
     ylab='Simulation Returns',
     ylim=ylim)
for (i in 2:ncol(cum_sim_df)) {
  lines(Date, t(cum_sim_df[i]), type='l')
}

# Porfolio Returns statistics at end of simulation
cum_final <- as.numeric( cum_sim_df[nrow(cum_sim_df),] )
cum_final_stats <- data.frame(mean   = mean(cum_final),
                        median = median(cum_final),
                        sd     = sd(cum_final))
print(cum_final_stats)

## Construct Confidential Intervals for returns
## first define function
ci <- function(df, conf) {
    # calculate confidence limit for specified confidence level
    # note specified conf = 1 - alpha
    # i.e., if want alpha=0.05 to get 95% conf limit, specify 0.95
    apply(df, 1, function(x) quantile(x, conf))
}
## create dataframe of confidence intervals
df <- cum_sim_df
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
