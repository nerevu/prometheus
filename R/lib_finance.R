#############################
#	Top Level Functions		#
#############################

###### returns all possible multisets ######
my_allocation <- function(max_assets, max_transactions=min/invest, invest=1000, min=100) {
	new_allocation <- create_allocation(max_assets, max_transactions)
	allocation_dbtable <- create_dbtable(new_allocation)
	allocation_dbtable <- nozero(allocation_dbtable)
	allocation_dataframe <- create_dataframe(allocation_dbtable)
} ##<-- end function -->

#####################
#	Scratch Pad		#
#####################
max_transactions <- 3
max_assets <- 3
max_samples <- 10
#my_allocation(max_assets)
#myarray <- new_allocation

#############################
#	Include Files			#
#############################
library(multic)

#############################
#	User Function Library	#
#############################

###### returns all possible multisets ######
create_multisets1 <- function(max_assets, max_transactions) {
	as.matrix(urnsamples(1:max_assets, size = max_transactions, ordered = FALSE, replace = TRUE))
} ##<-- end function -->

###### returns all possible multisets ######
create_multisets2 <- function(max_assets, max_transactions) {
	subsets(max_assets, max_transactions, allow.repeat=T)
} ##<-- end function -->

###### returns the number of multisets ######
get_num_multisets <- function(max_assets, max_transactions) {
	factorial((max_transactions + max_assets - 1))/(factorial(max_transactions)*factorial((max_assets - 1)))
} ##<-- end function -->

###### returns the number of multisets ######
get_num_multisets2 <- function(max_assets, max_transactions) {
	
} ##<-- end function -->

###### creates array of asset allocation possibilities ######
create_allocation <- function(max_assets, max_transactions) {
	num_multisets 	<- get_num_multisets(max_assets, max_transactions)
	max_multisets 	<- 1e6
	max_samples 	<- 1e3
	
	if (num_multisets < max_multisets) { ## calc all combinations
		arr_multisets <- create_multisets2(max_assets, max_transactions)
		arr_columns <- outer(1:num_multisets,rep(1, max_transactions))
		arr_allocations <- t(table(factor(arr_multisets),factor(arr_columns))/max_transactions)
	}  else { ## perform random sampling
		arr_allocations <- t(rmultinom(max_samples, max_transactions, rep(1, max_assets))/max_transactions)
	} ##<-- end if -->
	
	return(arr_allocations)
} ##<-- end function -->

###### convert array asset allocation table into a dataframe with labels ######
create_dataframe <- function(myarray) {
	myarray <- data.frame(scenario_id=myarray[,1], asset_class_ph_id=myarray[,2], allocation=myarray[,3])
} ##<-- end function -->

###### convert array asset allocation array into a format suitable for a database ######
create_dbtable <- function(myarray) {
	i <- 1
	max <- dim(myarray)[1]
	cols <- c(ncol(myarray),1)
	t_myarray <- t(myarray[i,])
	
	a <- array(1, dim=cols)
	b <- t(col(t_myarray))
	c <- array(t_myarray, dim=cols)
	new_array <- cbind(a,b,c)
	
	while(i < max){
		i <- i+1
		t_myarray <- t(myarray[i,])
		
		a <- array(i, dim=cols)
		b <- t(col(t_myarray))
		c <- array(t_myarray, dim=cols)
		z <- cbind(a,b,c)
		new_array <- rbind(new_array,z)
	} ##<-- end while -->
	
	return(new_array)
} ##<-- end function -->

###### remove assets with an allocation of zero from the array ######
nozero <- function(myarray) {
	myarray <- data.frame(myarray)
	myarray <- subset(myarray, X3 >0)
} ##<-- end function -->

npv <- function(x, i) {
	## purpose: to calculate the NPV
	## input: vector of adjusted cashflow value (numeric)
	## input: bisect length
	## calls: sppv()
	## output: numeric value
	## called_by: xirr
	
	## Example 1 ##
	# npv(rep(8792,12), 666.31/12) 
	# 15755.01 - 100000 - 10.0088%
	
	npv = c()
	
	for (k in 1:length(i)) {
		pvs = x * sppv(i[k], 1:length(x))
		npv = c(npv, sum(pvs))
	}
	
	return(npv)
}

sppv <- function(i, n) {
	## purpose: ?
	## input: vector of adjusted cashflow value (numeric)
	## input: bisect length
	## calls: none
	## output: numeric vector
	## called_by: npv()
  	
  	return((1 + i/100)^(-n))
}

xirr <- function(cashflow, dates, freq=30, guess=0, step=10, left=guess-step, right=guess+step, epsilon=1e-8) {
	## purpose: to calculate the internal rate of return for non-periodic cash flow
	## input: vector of cashflows (numeric)
	## input: vector of dates (string: format "%m-%d-%y")
	## input: output return frequency (daily=365, weekly=52, monthly=12, quarterly=4, annualized=1)
	## input: initial guess
	## input: step range
	## input: leftBracket value
	## input: rightBracket value
	## input: precision value
	## calls: sppv()
	## output: internal rate of return in the range [0,1]
	## called_by: ?
	
	## Example 1 ##
	# mycashflow <- c(-10000,2500, 2000, 3000,4000)
	# mydates <- c("01-12-87", "02-14-88", "03-03-88", "06-14-88", "12-01-88")
	# xirr(mycashflow, mydates)
	# 10.06%
	
	## Example 2 ##
	# mycashflow <- c(-10000,2750,4250,3250,2750)
	# mydates <- c("01-01-08","03-01-08","10-30-08","02-15-09","04-01-09")
	# xirr(mycashflow, mydates)
	# 37.34%
	
	if (length(cashflow) != length(dates)) {
		stop("length(cashflow) != length(dates)")
	}

	cashflow_adj <- c(cashflow[1])
	
	for (i in 1:(length(cashflow)-1)) {
		d1 <- as.Date(dates[i], "%m-%d-%y")
		d2 <- as.Date(dates[i+1], "%m-%d-%y")
		
		# There are no checks about the monotone values of dates
		interval <- as.integer(d2 - d1)
		cashflow_adj <- c(cashflow_adj, rep(0, interval-1), cashflow[i+1])
	}

	# Bisection method finding the rate to zero npv
	while (abs(right-left) > 2*epsilon) {
		midpoint = (right+left)/2
		if (npv(cashflow_adj, left) * npv(cashflow_adj, midpoint) > 0) {
			left = midpoint
		}
		else {right = midpoint}
	}

	# IRR for daily cashflow (not in percentage format)
	irr = (right+left) / 2 / 100  

	# Yield (return) reflecting compounding effect of daily returns
	irr <- (1 + irr) ^ (365/freq) - 1
	return(irr)
}

#############################
#	Buggy Functions			#
#############################

#############################
#	Incomplete Functions	#
#############################

calc_performance_disc <- function(PortfolioReturns, rf=0, p=0.95, freq=12) {
	## purpose: to calculate discrete portfolio risk/return statistics
	## inputs: database of investment, periods, and returns
	## inputs: risk free rate, in same period as returns
	## inputs: conﬁdence level for calculatio
	## inputs: frequency (daily=252, monthly=12, quarterly=4, annually=1)
	## calls: Mean()
	## calls: Variance()
	## calls: Kurtosity()
	## calls: Skewkess()
	## calls: SharpeRatio() -> PerformanceAnalytics 
	## calls: SharpeRatio.modified() -> PerformanceAnalytics 
	## calls: SortinoRatio() -> PerformanceAnalytics 
	## calls: Omega() -> PerformanceAnalytics 
	## output: array of investment, statistic, start date, end date, and value

	return(PortfolioPerfDisc)
}

calc_performance_cont <- function(PortfolioReturns, rf=0, p=0.95, freq=12) {
	## purpose: to calculate continuous portfolio risk/return statistics
	## inputs: database of investment, periods, and returns
	## inputs: risk free rate, in same period as returns
	## inputs: conﬁdence level for calculatio
	## inputs: frequency (daily=252, monthly=12, quarterly=4, annually=1)
	## calls: Sortino() -> ? 
	## calls: Omega() -> ?
	## calls: Kappa() -> ?
	## output: array of investment, statistic, and value

	return(PortfolioPerfCont)
}

calc_sortino <- function(PortfolioReturns) {
	## purpose: to calculate the Sortino Ratio over a range of MARs
	## inputs: array of investment, periods, and returns
	## output: array of investment, MAR, and SortinoRatio

	return(PortfolioSortino)
}

calc_xirr <- function(portfolio_cashflows, portfolio_cashflow_dates) {
	## purpose: to calculate my investment xirr (return)
	## input: dataframe of cash flows, tickers, and periods
	## input: dataframe of cash flow dates, tickers, and periods
	## calls: xirr()
	## output: dataframe of tickers, periods, and xirrs
	## called_by: ?
	
	return(PortfolioReturns)
}

create_faketransactions <- function(tradeperiods, myPortfolioMod, start_date, end_date, freq=12) {
	## purpose: to create the faketransactions table
	## input: data frame of period, start date, and end date
	## input: matrix of (positions, total cash flows, market prices, market values, and dates) by period by ticker
	## input: start date
	## input: end date
	## input: frequency (daily=252, monthly=12, quarterly=4, annually=1)
	## calls: none
	## output: data frame of quantity, market price, market value, activity, comission, cash flow, ticker, period, and date 
	## called_by: ?
	
	return(tradeperiods)
}

create_tradeperiods <- function(start_date, end_date, freq=12, mode=1) {
	## purpose: to create the periods table
	## input: start date
	## input: end date
	## input: frequency (daily=252, monthly=12, quarterly=4, annually=1)
	## input: mode (last trading day of period=1, first trading day of period=2)
	## calls: none
	## output: data frame of period, start date, and end date
	## called_by: ?
	
	return(tradeperiods)
}

gen_portfolio_cashflows <- function(CashFlows, start_date, end_date, freq=12, mode=1) {
	## purpose: to calculate cash flow values
	## input: database of cash flows, tickers, dates, and periods
	## input: start date
	## input: end date
	## input: frequency (daily=252, monthly=12, quarterly=4, annually=1)
	## input: mode (last trading day of period=1, first trading day of period=2)
	## calls: none
	## output: dataframe of cash flows, tickers, and periods
	## called_by: ? 
	
	return(portfolio_cashflows)
}
	
gen_portfolio_cashflow_dates <- function(CashFlows, start_date, end_date, freq=12, mode=1) {
	## purpose: to calculate cash flow dates
	## input: database of cash flows, tickers, dates, and periods
	## input: start date
	## input: end date
	## input: frequency (daily=252, monthly=12, quarterly=4, annually=1)
	## input: mode (last trading day of period=1, first trading day of period=2)
	## calls: none
	## output: dataframe of cash flow dates, tickers, and periods
	## called_by: ? 
	
	return(portfolio_cashflow_dates)
}

gen_tickers <- function(myPortfolio) {
	## purpose: to generate a list of tickers for my portfolio
	## input: array of tickers, positions, cost basis, cash flows, comissions, market prices, market values, and dates
	## calls: none
	## output: vector of tickers
	## called_by: ?
	
	return(tickers)
}

gen_trading_days <- function(start_date, end_date, freq=12, mode=1) {
	## purpose: to calculate trading day dates
	## input: start date
	## input: end date
	## input: frequency (daily=252, monthly=12, quarterly=4, annually=1)
	## input: mode (last trading day of period=1, first trading day of period=2)
	## calls: none
	## output: vector of trading day dates
	## called_by: ? 
	
	return(trading_days)
}

get_market_prices <- function(tickers, datelist, freq=12) {
	## purpose: to get portfolio missing stock prices
	## input: vector of tickers
	## input: start date
	## input: end date
	## input: quote frequency (daily=252, weekly=52, monthly=12, quarterly=4, annually=1)
	## calls: ? -> quantmod
	## output: array of tickers, quotes, and dates
	## called_by: ?

	return(newmarketprices)
}

myPortfolioMod <- function(myPortfolio, tradeperiods, mode=2) {
	## purpose: to convert a portfolio so that it is segmented by trade period [and ticker]
	## input: array of tickers, positions, cost basis, cash flows, comissions, market prices, market values, and dates
	## input: data frame of period, start date, and end date
	## input: array mode (by portfolio=1, by ticker=2)
	## calls: none
	## output(1): matrix of (tickers, positions, total cash flows, market prices, market values, and dates) by period
	## output(2): matrix of (positions, total cash flows, market prices, market values, and dates) by period by ticker
	## called_by: ?

	return(myPortfolioMod)
}

update_myPortfolio <- function(myPortfolio) {
	## purpose: to update the portfolio by filling in missing information
	## inputs: array of tickers, positions, cost basis, cash flows, comissions, market prices, market values, and dates with missing info
	## calls: ?
	## output: array of tickers, positions, cost basis, cash flows, comissions, market prices, market values, and dates with info filled in
	## called_by: ?

	return(myPortfolio)
}