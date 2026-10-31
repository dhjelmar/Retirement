# social security

# replace following with actuals
birth_yeard = 1900
birth_yeare = 1900   # e assumed to live longest
PIAd = 1             # d assumed to be the higher earner
PIAe = 1
g <- 0.0225    # cola growth rate = inflation
r <- 0.05      # MARR

pa <- function(g, r, n) {
  # g = geometric growth rate of payments
  # r = MARR
  # n = number of periods
  if ( g == r ) {
    return( n / (1+r) )
  } else {
    return( ( 1 - ( ( 1+g )/( 1+r ) )**n )/( r - g ) )
  }
}

factor <- function(months_late=NA, 
                   birth_month=NA, birth_year=NA, start_month=NA, start_year=NA) {
  # returns reduced social security payment for FRA=67 based on either of the following
  #     months_late = -# for months starting earlier than age 67
  #     birth and start months and years
  # months_late relative to FRA
  if ( is.na(months_late) ) {
    age_months <- (start_year - birth_year) * 12 + (start_month - birth_month)
    months_late <- age_months - 67*12
  }
  if ( months_late < 0 ) {
    # reduced by 5/9 of 1% for 1st 36 months then 5/1200 per month to month 60
    factor <- 1 - min(abs(months_late),36) * 5/900 - max(0,abs(months_late)-36) * 5/1200
  } else if ( months_late == 0 ) {
    # claiming at exactly age 67 and 0 months
    factor <- 1
  } else {
    factor <- 1 + months_late * 2/300
  }
  return(factor)
}

# New function to handle the factor for the surviving spouse (FRA=67)
# Note: Survivor benefits can be claimed as early as age 60 (84 months early).
# The maximum total reduction at age 60 is exactly 28.5% (meaning they receive 71.5% of PIA).
factor_survivor <- function(months_late=NA, 
                            birth_month=NA, birth_year=NA, start_month=NA, start_year=NA) {
  if ( is.na(months_late) ) {
    age_months <- (start_year - birth_year) * 12 + (start_month - birth_month)
    months_late <- age_months - 67*12
  }
  
  if ( months_late < 0 ) {
    # Survivor monthly reduction factor for FRA 67 is ~0.3392857% per month early.
    # Total reduction is capped at 28.5% at exactly 84 months early (Age 60).
    months_early <- min(abs(months_late), 84) 
    factor <- 1 - (months_early * (0.285 / 84))
  } else {
    # Survivor benefits do not earn Delayed Retirement Credits past FRA.
    factor <- 1.0
  }
  return(factor)
}

calculate_final_survivor_factor <- function(FACTORhigh, survivor_months_late) {
  # 1. Establish the RIB-LIM factor cap based on the deceased's claiming factor
  #    The floor is 0.825 (82.5%) of the deceased's PIA
  rib_lim_factor_cap <- max(FACTORhigh, 0.825)
  
  # 2. Get the survivor's baseline factor based on their own claiming age
  FACTORsurvivor <- factor_survivor(months_late = survivor_months_late)
  
  # 3. Apply the final rule (the lower of their age factor or the deceased's cap)
  actual_factor <- min(FACTORsurvivor, rib_lim_factor_cap)
  
  return(actual_factor)
}

###################
# replace above with

factor <- function(months_late) {
  # Vectorized worker retirement factor formula (FRA=67)
  ifelse(months_late < 0,
         1 - pmin(abs(months_late), 36) * 5/900 - pmax(0, abs(months_late) - 36) * 5/1200,
         ifelse(months_late == 0, 1, 1 + months_late * 2/300))
}

factor_survivor <- function(months_late) {
  # Vectorized survivor factor formula (FRA=67)
  ifelse(months_late < 0,
         1 - (pmin(abs(months_late), 84) * (0.285 / 84)),
         1.0)
}

calculate_final_survivor_factor <- function(FACTORhigh, survivor_months_late) {
  rib_lim_factor_cap <- pmax(FACTORhigh, 0.825)
  FACTORsurvivor <- factor_survivor(months_late = survivor_months_late)
  
  # Returns parallel minimum across vectors
  return(pmin(FACTORsurvivor, rib_lim_factor_cap))
}



####################

pv1 <- function(Ad, Ae, Sd, Se, Dd, De, g, r) {
  # PV based on monthly payments for Dave's assumed lifetime
  pvd <- Ad *   pa(g, r, n=Dd-Sd)
  # PV for Elsa would be hers up until Dave's assumed lifetime 
  # then increased to Dave's for remainder
  #pve <- Ae *   pa(g, r, n=De-Se)
  pve <- Ae *   pa(g, r, n=Dd-Se)   +
          Ad * ( pa(g, r, n=De-Se) - pa(g, r, n=Dd-Se) )
  pv <- pvd + pve
  cat(' PV D  =', scales::dollar(trunc(pvd)), '\n',
       'PV E  = ', scales::dollar(trunc(pve)), '\n',
       'PV PV =', scales::dollar(trunc(pv)))
  #return(list(pv=pv, pvd=pvd, pve=pve))
}

pv <- function(PIAd, PIAe, Sd, Se, Dd, De, g, r,
               current_year=current_year,
	       birth_yeard=birth_yeard, birth_yeare=birth_yeare) {
  
  # reduced or increased benefit amount
  months_lated=(Sd-67)*12
  months_latee=(Se-67)*12
  factord <- factor(months_late=months_lated)
  factore <- factor(months_late=months_latee)
  Ad <- PIAd * factord
  Ae <- PIAe * factore
  cat(' Starting: PIA D      =', scales::dollar(trunc(PIAd)), 'per month\n',
       '          PIA E      =', scales::dollar(trunc(PIAe)), 'per month\n',
       '          Payment D  =', scales::dollar(trunc(Ad)), 'per month\n',
       '          Payment E  =', scales::dollar(trunc(Ae)), 'per month\n')
      
  # initialize parameters and loop through years
  pvd <- 0
  pve <- 0
  n <- 0
  total <- 0
  mylist <- list()
  for ( year in current_year:max(birth_yeard+Dd, birth_yeare+De) ) {
    n <- n + 1
    aged <- year - birth_yeard
    agee <- year - birth_yeare
    
    if ( (aged>=Sd)&(aged<=Dd)) {
      # PV based on monthly payments for D's assumed lifetime
      if ( aged == Sd ) {
        # this is the first payment year so only 8 months of payments
        paymentd = floor(Ad*8  * (1+g)^n)
      } else {
        paymentd = floor(Ad*12 * (1+g)^n)
      }
      total <- total + paymentd
      pvd <- pvd + paymentd / (1+r)^n 
    } else {
      paymentd <- 0.
    }
    
    if ( (agee>=Se)&(agee<=De)) {
      # PV for E would be hers up until D's assumed lifetime 
      # then increased to D's for remainder
      if ( aged<=Dd ) {
        # D still alive
        if ( agee == Se ) {
          # start year is less than a full year of payments
          paymente = floor(Ae*10 * (1+g)^n)
        } else {
          paymente = floor(Ae*12 * (1+g)^n)
        }
      } else {
        # D not alive
        factor_survivor <- calculate_final_survivor_factor(factord, months_latee)
        paymente = floor(factor_survivor * Ad * (1+g)^n)
      }
      total <- total + paymente
      pve <- pve + paymente / (1+r)^n 
    } else {
      paymente <- 0.
    }
    
    pv <- pvd + pve
    
    mydict_item <- list(
      year = year,
      aged = aged,
      agee = agee,
      Sd = Sd,
      Se = Se,
      Dd = Dd,
      De = De,
      paymentd = round(paymentd,0),
      paymente = round(paymente,0),
      pvd = round(pvd,0),
      pve = round(pve,0),
      pv = pv,
      total = total
    )
    mylist[[n]] <- mydict_item
  }
  
  # convert to dataframe
  # df <- data.table::rbindlist(mylist)   # data.table more efficient but not installed
  df <- do.call(rbind.data.frame, mylist)
  
  cat(' Ending:   PV D       =', scales::dollar(trunc(pvd)), '\n',
       '          PV E       =', scales::dollar(trunc(pve)), '\n',
       '          PV PV      =', scales::dollar(trunc(pv)), '\n',
       '          Total      =', scales::dollar(trunc(total)))
  
  return(df)
}

df1 <- pv(PIAd=PIAd, PIAe=PIAe, Sd=70, Se=70, Dd=94, De=99, g=g, r=r)
tail(df1)
pv1(PIAd=PIAd, PIAe=PIAe, Sd=70, Se=70, Dd=94, De=99, g=g, r=r)
pv1(PIAd=PIAd, PIAe=PIAe, Sd=70, Se=70, Dd=94, De=99, g=0, r=0)

df2 <- pv(PIAd=PIAd, PIAe=PIAe, Sd=67, Se=67, Dd=94, De=99, g=g, r=r)
tail(df2)

df3 <- pv(PIAd=PIAd, PIAe=PIAe, Sd=62, Se=62, Dd=94, De=99, g=g, r=r)
tail(df3)

df4 <- pv(PIAd=PIAd, PIAe=PIAe, Sd=70, Se=62, Dd=94, De=99, g=g, r=r)
tail(df4)

df5 <- pv(PIAd=PIAd, PIAe=PIAe, Sd=70, Se=67, Dd=94, De=99, g=g, r=r)
tail(df5)

xvar <- 'agee'
xlab <- "Age E"
ylim <- range(df1$pv, df2$pv, df3$pv, df4$pv, df5$pv)/1E6
with(df1, plot(unlist(df1[xvar]), pv/1E6, col='black', type='l', ylim=ylim, 
               xlab=xlab, ylab='Present Value, $M',
               main=paste('MARR =',r)))
lines(unlist(df2[xvar]), df2$pv/1E6, col='red')     
lines(unlist(df3[xvar]), df3$pv/1E6, col='cyan')     
lines(unlist(df4[xvar]), df4$pv/1E6, col='purple')     
lines(unlist(df5[xvar]), df5$pv/1E6, col='orange')     
legend('bottomright', 
       legend=c('D 70; E 70','D 67; E 67','D 62; E 62','D 70; E 62','D 70; E 67'), 
       col=c('black', 'red', 'cyan', 'purple', 'orange'),
       lty=c(1,1,1,1,1))

# extract last row of each dataframe
df_list <- list(df1, df2, df3, df4, df5)
result_df <- do.call(rbind, lapply(df_list, tail, n = 1))
pv7070 <- result_df$pv[(result_df$Sd==70)&(result_df$Se==70)]
result_df$pv_diff <- round(result_df$pv - pv7070, 0)
print(result_df)
