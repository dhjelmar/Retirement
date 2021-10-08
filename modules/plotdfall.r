set.seed(1)
DF <- data.frame(2000:2009,matrix(rnorm(50, 1000, 200), ncol=5))
colnames(DF) <- c('Year', paste0('Country', 2:ncol(DF)))
DF.TS <- ts(DF[-1], start = 2000, frequency = 1)
DF.TS
# All countries in one plot... colorful, common scale, and so on
plot(DF.TS, plot.type="single", col = 1:ncol(DF.TS))
legend("bottomleft", colnames(DF.TS), col=1:ncol(DF), lty=1, cex=.65)

# All countries in one plot... colorful, common scale, and so on
plot(twr, plot.type="single", col = 1:ncol(twr))
legend("bottomleft", legend=colnames(twr), col=1:ncol(twr), lty=1, cex=.65)
data.frame(symbols=colnames(twr), color=palette()[1:ncol(twr)])
mtext(text='test', side=3)

plot(twr[,which(grepl('SPY', colnames(twr)))], plot.type="single", col = 1:ncol(twr))


# All countries in one plot... colorful, common scale, and so on
twrts <- as.ts(twr)
plot(twrts, plot.type="single", col = 1:ncol(twrts))
legend("topleft", legend=colnames(twrts), col=1:ncol(twrts), lty=1, cex=.65)
grid(col='grey70')


plotxts <- function(xts) {
    date <- zoo::index(xts)
    matplot(x=date, type='l', xaxt='n')

timelabels<-format(timestamp,"%H:%M")
axis(1,at=timestamp,labels=timelabels)
    
    grid(col='grey70')
    legend('topleft',
           legend = names(xts),
           col    = 1:ncol(xts),
           lty    = 1)
}

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

out <- equityget(c('SPY', 'IWM', 'EFA', 'AGG', 'SHV'), from='1995-01-01', period='years')
twr <- out$twr
twrdf <- as.data.frame(twr)
twrdf$date <- as.Date( rownames(twrdf) )
plotdfall(twrdf, 'date', size=1)
