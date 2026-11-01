# social security

# replace following with actuals
birth_year1 = 1900
birth_year2 = 1900   # e assumed to live longest
PIA1 = 1             # d assumed to be the higher earner
PIA2 = 1
g <- 0.0225    # cola growth rate = inflation
r <- 0.05      # MARR

current_year = 2027
birth_year1 = 1965
birth_year2 = 1964   # e assumed to live longest
PIA1 = 4220             # d assumed to be the higher earner
PIA2 = 2930

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

# factor <- function(months_late=NA, 
#                    birth_month=NA, birth_year=NA, start_month=NA, start_year=NA) {
#   # returns reduced social security payment for FRA=67 based on either of the following
#   #     months_late = -# for months starting earlier than age 67
#   #     birth and start months and years
#   # months_late relative to FRA
#   if ( is.na(months_late) ) {
#     age_months <- (start_year - birth_year) * 12 + (start_month - birth_month)
#     months_late <- age_months - 67*12
#   }
#   if ( months_late < 0 ) {
#     # reduced by 5/9 of 1% for 1st 36 months then 5/1200 per month to month 60
#     factor <- 1 - min(abs(months_late),36) * 5/900 - max(0,abs(months_late)-36) * 5/1200
#   } else if ( months_late == 0 ) {
#     # claiming at exactly age 67 and 0 months
#     factor <- 1
#   } else {
#     factor <- 1 + months_late * 2/300
#   }
#   return(factor)
# }
# 
# # New function to handle the factor for the surviving spouse (FRA=67)
# # Note: Survivor benefits can be claimed as early as age 60 (84 months early).
# # The maximum total reduction at age 60 is exactly 28.5% (meaning they receive 71.5% of PIA).
# factor_survivor <- function(months_late=NA, 
#                             birth_month=NA, birth_year=NA, start_month=NA, start_year=NA) {
#   if ( is.na(months_late) ) {
#     age_months <- (start_year - birth_year) * 12 + (start_month - birth_month)
#     months_late <- age_months - 67*12
#   }
#   
#   if ( months_late < 0 ) {
#     # Survivor monthly reduction factor for FRA 67 is ~0.3392857% per month early.
#     # Total reduction is capped at 28.5% at exactly 84 months early (Age 60).
#     months_early <- min(abs(months_late), 84) 
#     factor <- 1 - (months_early * (0.285 / 84))
#   } else {
#     # Survivor benefits do not earn Delayed Retirement Credits past FRA.
#     factor <- 1.0
#   }
#   return(factor)
# }
# 
# calculate_final_survivor_factor <- function(FACTORhigh, survivor_months_late) {
#   # 1. Establish the RIB-LIM factor cap based on the deceased's claiming factor
#   #    The floor is 0.825 (82.5%) of the deceased's PIA
#   rib_lim_factor_cap <- max(FACTORhigh, 0.825)
#   
#   # 2. Get the survivor's baseline factor based on their own claiming age
#   FACTORsurvivor <- factor_survivor(months_late = survivor_months_late)
#   
#   # 3. Apply the final rule (the lower of their age factor or the deceased's cap)
#   actual_factor <- min(FACTORsurvivor, rib_lim_factor_cap)
#   
#   return(actual_factor)
# }

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

pv1 <- function(PIA1, PIA2, S1, S2, D1, D2, g, r) {
  # PV based on monthly payments for Dave's assumed lifetime
  A1 <- PIA1 * factor(months_late=(S1-67)*12)
  pv1 <- 12 * A1 *   pa(g, r, n=D1-S1)
  # PV for Elsa would be hers up until Dave's assumed lifetime 
  # then increased to Dave's for remainder
  #pve <- Ae *   pa(g, r, n=De-Se)
  A2 <- PIA2 * factor(months_late=(S2-67)*12)
  pv2 <- 12 * A2 *   pa(g, r, n=D1-S2)   +
         12 * A1 * ( pa(g, r, n=D2-S2) - pa(g, r, n=D1-S2) )
  pv <- pv1 + pv2
  cat(' PV D  =', scales::dollar(trunc(pv1)), '\n',
       'PV E  = ', scales::dollar(trunc(pv2)), '\n',
       'PV PV =', scales::dollar(trunc(pv)))
  #return(list(pv=pv, pvd=pvd, pve=pve))
}

pv <- function(PIA1, PIA2, S1, S2, D1, D2, g, r, current_year, birth_year1, birth_year2) {
  
  # simulation assumes person 1 is the larger earner and dies the same time or before person 2
    
  # reduced or increased benefit amount
  months_lated=(S1-67)*12
  months_latee=(S2-67)*12
  factord <- factor(months_late=months_lated)
  factore <- factor(months_late=months_latee)
  A1 <- PIA1 * factord
  A2 <- PIA2 * factore
  cat(' Starting: PIA 1      =', scales::dollar(trunc(PIA1)), 'per month\n',
       '          PIA 2      =', scales::dollar(trunc(PIA2)), 'per month\n',
       '          Payment 1  =', scales::dollar(trunc(A1)), 'per month\n',
       '          Payment 2  =', scales::dollar(trunc(A2)), 'per month\n')
      
  # initialize parameters and loop through years
  pv1 <- 0
  pv2 <- 0
  n <- 0
  total <- 0
  mylist <- list()
  for ( year in current_year:max(birth_year1+D1, birth_year2+D2) ) {
    n <- n + 1
    age1 <- year - birth_year1
    age2 <- year - birth_year2
    
    if ( (age1>=S1)&(age1<=D1)) {
      # PV based on monthly payments for D's assumed lifetime
      if ( age1 == S1 ) {
        # this is the first payment year so only 8 months of payments
        payment1 = floor(A1*8  * (1+g)^n)
      } else {
        payment1 = floor(A1*12 * (1+g)^n)
      }
      total <- total + payment1
      pv1 <- pv1 + payment1 / (1+r)^n 
    } else {
      payment1 <- 0.
    }
    
    if ( (age2>=S2)&(age2<=D2)) {
      # PV for E would be hers up until D's assumed lifetime 
      # then increased to D's for remainder
      if ( age1<=D1 ) {
        # D still alive
        if ( age2 == S2 ) {
          # start year is less than a full year of payments
          payment2 = floor(A2*10 * (1+g)^n)
        } else {
          payment2 = floor(A2*12 * (1+g)^n)
        }
      } else {
        # D not alive
        factor_survivor <- calculate_final_survivor_factor(factord, months_latee)
        payment2 = floor(factor_survivor * A1 * (1+g)^n)
      }
      total <- total + payment2
      pv2 <- pv2 + payment2 / (1+r)^n 
    } else {
      payment2 <- 0.
    }
    
    pv <- pv1 + pv2
    
    mydict_item <- list(
      year = year,
      age1 = age1,
      age2 = age2,
      S1 = S1,
      S2 = S2,
      D1 = D1,
      D2 = D2,
      payment1 = round(payment1,0),
      payment2 = round(payment2,0),
      pv1 = round(pv1,0),
      pv2 = round(pv2,0),
      pv = pv,
      total = total
    )
    mylist[[n]] <- mydict_item
  }
  
  # convert to dataframe
  # df <- data.table::rbindlist(mylist)   # data.table more efficient but not installed
  df <- do.call(rbind.data.frame, mylist)
  
  cat(' Ending:   PV 1       =', scales::dollar(trunc(pv1)), '\n',
       '          PV 2       =', scales::dollar(trunc(pv2)), '\n',
       '          PV PV      =', scales::dollar(trunc(pv)), '\n',
       '          Total      =', scales::dollar(trunc(total)))
  
  return(df)
}


scenario <- function(g, r) {
    df1 <- pv(PIA1=PIA1, PIA2=PIA2, S1=70, S2=70, D1=94, D2=99, g=g, r=r,
              current_year=current_year, birth_year1=birth_year1, birth_year2=birth_year2)
    tail(df1)
    pv1(PIA1=PIA1, PIA2=PIA2, S1=70, S2=70, D1=94, D2=99, g=g, r=r)
    pv1(PIA1=PIA1, PIA2=PIA2, S1=70, S2=70, D1=94, D2=99, g=0, r=0)
    
    df2 <- pv(PIA1=PIA1, PIA2=PIA2, S1=67, S2=67, D1=94, D2=99, g=g, r=r,
              current_year=current_year, birth_year1=birth_year1, birth_year2=birth_year2)
    tail(df2)
    
    df3 <- pv(PIA1=PIA1, PIA2=PIA2, S1=62, S2=62, D1=94, D2=99, g=g, r=r,
              current_year=current_year, birth_year1=birth_year1, birth_year2=birth_year2)
    tail(df3)
    
    df4 <- pv(PIA1=PIA1, PIA2=PIA2, S1=70, S2=62, D1=94, D2=99, g=g, r=r,
              current_year=current_year, birth_year1=birth_year1, birth_year2=birth_year2)
    tail(df4)
    
    df5 <- pv(PIA1=PIA1, PIA2=PIA2, S1=70, S2=67, D1=94, D2=99, g=g, r=r,
              current_year=current_year, birth_year1=birth_year1, birth_year2=birth_year2)
    tail(df5)
    
    xvar <- 'age2'
    xlab <- "Age2"
    ylim <- range(df1$pv, df2$pv, df3$pv, df4$pv, df5$pv)/1E6
    par(bg='grey90')
    with(df1, plot(unlist(df1[xvar]), pv/1E6, col='black', type='l', ylim=ylim, 
                   xlab=xlab, ylab='Present Value, $M',
                   main=paste('MARR =',r)))
    lines(unlist(df2[xvar]), df2$pv/1E6, col='red')     
    lines(unlist(df3[xvar]), df3$pv/1E6, col='purple')     
    lines(unlist(df4[xvar]), df4$pv/1E6, col='black', lty=2)     
    lines(unlist(df5[xvar]), df5$pv/1E6, col='red', lty=2)     
    legend('bottomright', 
           legend=c('D 70; E 70','D 67; E 67','D 62; E 62','D 70; E 62','D 70; E 67'), 
           col=c('black', 'red', 'purple', 'black', 'red'),
           lty=c(1,1,1,2,2))
    grid(col='grey70')
    
    # extract last row of each dataframe
    df_list <- list(df1, df2, df3, df4, df5)
    result_df <- do.call(rbind, lapply(df_list, tail, n = 1))
    pv7070 <- result_df$pv[(result_df$S1==70)&(result_df$S2==70)]
    result_df$pv_diff <- round(result_df$pv - pv7070, 0)
    print(result_df)
    
    return(list(df1=df1,df2=df2,df3=df3,df4=df4,df5=df5,dfsum=result_df))
}

par(mfrow=c(3,1))
out1 <- scenario(g=0.025, r=0.05)
out2 <- scenario(g=0.025, r=0.07)
out3 <- scenario(g=0.025, r=0.10)
