plotdfall <- function(df, xx, size=0.01, type='b', legendloc='topleft') {
    ## plots every parameter in df as a function of x on single plot
    ## df      = dataframe
    ## xx      = x-axis variable to be specified in quotes
    ## size    = datapoint size (0.01 default to not see points but still get line color)
    ## type    = 'p' for points
    ##         = 'l' for lines     <-- creates a single line so only black
    ##         = 'b' for both      <-- same as above
    
    ## determine location of xx in the dataframe
    xxcol <- which(grepl(xx, names(df)))  ## xx column
    xx1   <- df[, xxcol]                  ## xx values

    ## first sort the data by xx in case want lines
    df <- df[order(df[xxcol]),]

    ## use melt to create new df with columns: index, series, and value
    ## where every column of old df is now in column value with the
    ## name of the column in series
    df <- reshape2::melt(df, id.vars=xx, variable.name='series')

    ## need to plot points and not just line to get color using df$series
    ## do not actually want points, so plotting them small with cex=0.01
    plot(df[1], df$value, col=df$series,
         cex=size, lty=1, type=type,
         xlab=xx, ylab='value')
    grid(col='grey70')
    legend(legendloc,
           legend = unique(df$series),
           col    = 1:length(df$series),
           lty    = 1)
}

#plotdfall(mtcars, 'mpg', legendloc='topright', type='b')
# a <- seq(10,1,-1)
# b <- seq(21,30)
# c <- seq(41,50)
# df <- data.frame(a,b,c)
# plotdfall(df, 'a')



#d <- rep('type1', 5)
#d2 <- rep('type2', 5)
#d <- c(d, d2)
#df <- data.frame(a,b,c,d)

#plotspace(1,2)
#plotdfall(mtcars, 'mpg', legendloc='topright', type='b')
#df <- select(mtcars, mpg, hp)
#plotdfall(df, 'mpg', legendloc='topright', type='b')

## out <- equityget(c('SPY', 'IWM', 'EFA', 'AGG', 'SHV'), from='1995-01-01', period='years')
## twr <- out$twr
## twrdf <- as.data.frame(twr)
## twrdf$date <- as.Date( rownames(twrdf) )
## plotdfall(twrdf, 'date', size=1)
