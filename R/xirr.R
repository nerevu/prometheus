#~ Title: XIRR Excel function simulation
#~ 
#~ Reference 1: How to manage irregular intervals - http://www.geocities.com/accessreddy/excel/xirr.htm
#~ Reference 2: How to calculate IRR manually - http://www.s-anand.net/Calculating_IRR_manually.html
#~ 
#~ Step 1: enter zeroes (0) against dates that do not have any cash outflow or inflows.
#~ Step 1bis: calculate IRR for these cash flow values using normal IRR function.
#~ Step 1tris: or using an iteractive approach as bisection method to find the NPV zeroes.
#~ Step 2: multiply this value of IRR by 365 to get annual IRR (since, these are daily cash flows).
#~ Step 3: refine using the formula =( 1+ R / 365) ^ 365 - 1), where R is the the value obtained in Step2.

#~ npv(rep(8792,12), 666.31/12) # 15755.01 - 100000 - 10.0088%

# the correct IRR is 10.06% - source: matlab example
mycashflow <- c(-10000,2500, 2000, 3000,4000)
mydates <- c("12-01-87", "14-02-88", "03-03-88", "14-06-88", "01-12-88")
xirr(mycashflow, mydates)

# the correct IRR is 37.34% - source: microsoft example
mycashflow <- c(-10000,2750,4250,3250,2750)
mydates <- c("1-01-08","1-03-08","30-10-08","15-02-09","1-04-09")
xirr(mycashflow, mydates)
