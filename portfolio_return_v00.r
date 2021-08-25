## https://israeldi.github.io/bookdown/_book/monte-carlo-simulation-of-stock-portfolio-in-r-matlab-and-python.html

source('/home/dlhjel/GitHub_repos/R-setup/setup.r')

data <- '
    Date AAPL_Adj_Close GOOG_Adj_Close FB_Adj_Close
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
stock_Data = readall(data)
stock_Price = as.matrix( stock_Data[ , 2:4] )

mc_rep = 10 # Number of Monte Carlo Simulations
training_days = 5

# This function returns the first differences of a t x q matrix of data
returns = function(Y){
  len = nrow(Y)
  yDif = Y[2:len, ] / Y[1:len-1, ] - 1
}

# Get the Stock Returns
stock_Returns = returns(stock_Price)

# Suppose we invest our money evenly among all three assets 
# We use today's Price 11/14/2018 to find the number of shares each stock 
# that we buy
portfolio_Weights = t(as.matrix(rep(1/ncol(stock_Returns), ncol(stock_Returns))))
print(portfolio_Weights)

# Get the Variance Covariance Matrix of Stock Returns
pairs(stock_Returns)
coVarMat = cov(stock_Returns)

# calculate meaan return for each stock
miu = colMeans(stock_Returns)
# Extend the vector to a matrix
Miu = matrix(rep(miu, training_days), nrow = 3)

# Initializing simulated 30 day portfolio returns
portfolio_Returns_30_m = matrix(0, training_days, mc_rep)

set.seed(200)
for (i in 1:mc_rep) {
  Z = matrix ( rnorm( dim(stock_Returns)[2] * training_days ), ncol = training_days )
  # Lower Triangular Matrix from our Choleski Factorization
  L = t( chol(coVarMat) )
  # Calculate stock returns for each day
  daily_Returns = Miu + L %*% Z  
  # Calculate portfolio returns for 30 days
  portfolio_Returns_30 = cumprod( portfolio_Weights %*% daily_Returns + 1 )
  # Add it to the monte-carlo matrix
  portfolio_Returns_30_m[,i] = portfolio_Returns_30;
}

# Visualising result
x_axis = rep(1:training_days, mc_rep)
y_axis = as.vector(portfolio_Returns_30_m-1)
plot_data = data.frame(x_axis, y_axis)
ggplot(data = plot_data, aes(x = x_axis, y = y_axis)) + geom_path(col = 'red', size = 0.1) +
  xlab('Days') + ylab('Portfolio Returns') + 
  ggtitle('Simulated Portfolio Returns in 30 days')+
  theme_bw() +
    theme(plot.title = element_text(hjust = 0.5))

# Porfolio Returns statistics on the 30th day.
Avg_Portfolio_Returns = mean(portfolio_Returns_30_m[30,]-1)
SD_Portfolio_Returns = sd(portfolio_Returns_30_m[30,]-1)
Median_Portfolio_Returns = median(portfolio_Returns_30_m[30,]-1)
print(c(Avg_Portfolio_Returns,SD_Portfolio_Returns,Median_Portfolio_Returns))

# Construct a 95% Confidential Interval for average returns
Avg_CI = quantile(portfolio_Returns_30_m[30,]-1, c(0.025, 0.975))
print(Avg_CI)
