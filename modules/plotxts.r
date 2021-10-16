plotxts <- function(xts, legendloc='topleft') {
    ## plots every column in the XTS object vs. date and adds a legend
    ylabel  <- deparse(substitute(xts))
    xts::plot.xts(xts, ylab=ylabel)
    xts::addLegend(legendloc,
                   legend.names = names(xts), 
                   lty=1,
                   col=1:ncol(xts))
}

plotzoo <- function(zoo, legendloc='topleft') {
    ## plots every column in the ZOO object vs. date and adds a legend
    ## seems to work on zoo and xts objects
    ylabel  <- deparse(substitute(zoo))
    zoo::plot.zoo(zoo,
                  ylab=ylabel,
                  screens=1,
                  lty=1,
                  col=1:ncol(zoo))
    legend(legendloc,
           legend = names(zoo), 
           lty    = 1,
           col    = 1:ncol(zoo))
}


plotmat <- function(mat, xx=NULL, legendloc='topleft') {

    ## work in progress

    ## plot matrix vs. xx
    ## strip out xx column if specified and part of mat
    
    ## Add argument axes=F to omit the axes
    if (!is.null(xx)) {
        xlabel <- deparse(substitute(xx))
    } else {
        xlabel <- 'Index'
        xx     <- 1:nrow(mat)
    }
    if (xts::is.xts(mat) == TRUE | zoo::is.zoo(mat)) {
        ## xts or zoo passed in rather than matrix
        ## use dates for x-axis (override xx if specified)
        xx     <- zoo::index(mat)
        xlabel <- 'Date'
        mat    <- as.matrix(mat)
    } else if (is.data.frame(mat) == TRUE) {
        ## dataframe passed in rather than matrix
        if (!is.null(xx)) {
            ## xx is specified so handle it
            ncolxx <- which(grepl(xx, names(mat)))
            if (length(ncolxx) > 0) {
                ## xx is in mat so not need to remove it
                xx     <- mat$xx
                mat$xx <- NULL
            }
            xlabel <- deparse(substitute(xx))
        }
        mat    <- as.matrix(mat)
    }
    ylabel  <- deparse(substitute(mat))

    graphics::matplot(x=xx, y=mat, type='l',
                      xlab = xlabel,
                      ylab = ylabel)
    grid(col='grey70')
    legend(legendloc,
           legend = names(mat),
           col    = 1:ncol(mat),
           lty    = 1)

}


## ## test that does not use any of my functions
## quantmod::getSymbols(c('SPY','IWM'),
##                      src  = 'yahoo', 
##                      from = '2010-01-01', 
##                      to   = '2021-02-01',
##                      auto.assign = TRUE, 
##                      warnings = FALSE)
## close <- cbind(SPY$SPY.Close, IWM$IWM.Close)
## plotxts(close)

## ## test that relies on my function equityget
## out   <- equityget(c('SPY', 'IWM', 'EFA', 'AGG', 'SHV'), from='1995-01-01', period='years')
## close <- out$close
## plotxts(close)



##-----------------------------------------------------------------------------
## following were earlier attempts that I can probably get rid of 
##-----------------------------------------------------------------------------

## ## FOLLOWING SUBMITTED TO STACKEXCHANGE
## ## https://stackoverflow.com/questions/69498375/in-r-how-can-i-add-a-legend-to-a-plot-of-an-xts-object
## ## create XTS object with two columns
## quantmod::getSymbols(c('SPY','IWM'),
##                      src  = 'yahoo', 
##                      from = '2010-01-01', 
##                      to   = '2021-02-01',
##                      auto.assign = TRUE, 
##                      warnings = FALSE)
## close <- cbind(SPY$SPY.Close, IWM$IWM.Close)
## 
## ## the following works except for the legend
## qualityTools::plot(close, col=1:ncol(close))
## legend('topleft', legend=colnames(close), col=1:ncol(close), lty=1, cex=0.5)
## 
## ## the following works but destroys the time axis
## closets <- stats::as.ts(close)
## qualityTools::plot(closets, plot.type='single', col = 1:ncol(closets))
## legend("topleft", legend=colnames(closets), col=1:ncol(closets), lty=1, cex=0.5)
## 
## ##-----------------------------------------------------------------------------


## plot(twr, plot.type="single", col = 1:ncol(twr))
## legend("bottomleft", legend=colnames(twr), col=1:ncol(twr), lty=1, cex=.65)

## plot(twr[,which(grepl('SPY', colnames(twr)))], plot.type="single", col = 1:ncol(twr))


## # All countries in one plot... colorful, common scale, and so on
## twrts <- as.ts(twr)
## plot(twrts, plot.type="single", col = 1:ncol(twrts))
## legend("topleft", legend=colnames(twrts), col=1:ncol(twrts), lty=1, cex=.65)
## grid(col='grey70')

## plotxts <- function(xts) {
## 
##     ## ## try matplot
##     ## date <- zoo::index(xts)
##     ## graphics::matplot(x=date, y=xts, type='l')
##     ## grid(col='grey70')
##     ## legend('topleft',
##     ##        legend = names(xts),
##     ##        col    = 1:ncol(xts),
##     ##        lty    = 1)
##     
##     ## ## try matplot
##     ## date <- zoo::index(xts)
##     ## graphics::matplot(x=date, y=xts, type='l', xaxt='n')
##     ## axis(side=1, at=1:nrow(xts), labels=date)
##     ## grid(col='grey70')
##     ## legend('topleft',
##     ##        legend = names(xts),
##     ##        col    = 1:ncol(xts),
##     ##        lty    = 1)
## 
##     ## try matplot (THIS ONE IS NOT BAD)
##     ## Add argument axes=F to omit the axes
##     date <- zoo::index(xts)
##     ylabel  <- deparse(substitute(xts))
##     graphics::matplot(xts, type='l', lty=1, 
##                       main=NULL, xlab='date', ylab=ylabel,
##                       axes=FALSE)
##     axis(side=1, at=1:nrow(xts), labels=date)   # x-axis
##     axis(side=2)                                # y-axis
##     grid(col='grey70')
##     legend('topleft',
##            legend = names(xts),
##            col    = 1:ncol(xts),
##            lty    = 1)
## 
##     ## ## the following works except for the legend
##     ## ## also, it only works interatively (i.e., not in a function)
##     ## qualityTools::plot(xts, col=1:ncol(xts))
##     ## legend('topleft', legend=colnames(xts), col=1:ncol(xts), lty=1, cex=0.5)
##     ## data.frame(symbols=colnames(twr), color=palette()[1:ncol(twr)])
##     ## mtext(text='test', side=3)
## 
##     ## ## the following works but uses a fake time axis
##     ## ## (1 increment for each period; may not be bad)
##     ## xtsts <- stats::as.ts(xts)
##     ## qualityTools::plot(xtsts, plot.type='single', col = 1:ncol(xtsts), xaxt='n')
##     ## legend("topleft", legend=colnames(xtsts), col=1:ncol(xtsts), lty=1, cex=0.5)
##     ## axis(1, at=1:nrow(xtsts), labels=date)
##     ## grid(col='grey70')
##     
##     
##     }
## test
## quantmod::getSymbols(c('SPY','IWM'),
##                      src  = 'yahoo', 
##                      from = '2010-01-01', 
##                      to   = '2021-02-01',
##                      auto.assign = TRUE, 
##                      warnings = FALSE)
## close <- cbind(SPY$SPY.Close, IWM$IWM.Close)
## plotxts(close)
