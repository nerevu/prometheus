<?php
//*****************************************************************************//
// Some tock keywords:
// ^DJI		 - Dow Jones
// ^IXIC	 - Nasdaq
// ^GSPC	 - S&P 500
// ^STOXX50E - Euro STOXX50
// For more stock keywords visit http://finance.yahoo.com
//
// The download operation is efficient: only one request is made even if
// several symbols are requested at once. The return value of
// is an array, with the following elements:
//
// 0 Symbol
// 1 Company Name
// 2 Last Price
// 3 Last Trade Date
// 4 Last Trade Time
// 5 Change
// 6 Percent Change
// 7 Volume
// 8 Average Daily Vol
// 9 Bid
// 10 Ask
// 11 Previous Close
// 12 Today's Open
// 13 Day's Range
// 14 52-Week Range
// 15 Earnings per Share
// 16 P/E Ratio
// 17 Dividend Pay Date
// 18 Dividend per Share
// 19 Dividend Yield
// 20 Market Capitalization
// 21 Stock Exchange
//
// If the extended format has been selected, the following fields are also
// retrieved:
//
// 22 Short ratio
// 23 1yr Target Price
// 24 EPS Est. Current Yr
// 25 EPS Est. Next Year
// 26 EPS Est. Next Quarter
// 27 Price/EPS Est. Current Yr
// 28 Price/EPS Est. Next Yr
// 29 PEG Ratio
// 30 Book Value
// 31 Price/Book
// 32 Price/Sales
// 33 EBITDA
// 34 50-day Moving Avg
// 35 200-day Moving Avg
//
// If the realtime format has been selected, the following fields are also
// retrieved:
//
// 22 Ask (real-time)
// 23 Bid (real-time)
// 24 Change in Percent (real-time)
// 25 Last trade with time (real-time)
// 26 Change (real-time)
// 27 Day range (real-time)
// 28 Market-cap (real-time)
//
// The following list contains all the available data fields at Yahoo!
// along with the corresponding format string entry:
//
// Symbol							s
// Name								n
// Last Trade (With Time)			l
// Last Trade (Price Only)			l1
// Last Trade Date					d1
// Last Trade Time					t1
// Last Trade Size					k3
// Change and Percent Change		c
// Change							c1
// Change in Percent				p2
// Ticker Trend						t7
// Volume							v
// Average Daily Volume				a2
// More Info						i
// Trade Links						t6
// Bid								b
// Bid Size							b6
// Ask								a
// Ask Size							a5
// Previous Close					p
// Open								o
// Day's Range						m
// 52-week Range					w
// Change From 52-wk Low			j5
// Pct Chg From 52-wk Low			j6
// Change From 52-wk High			k4
// Pct Chg From 52-wk High			k5
// Earnings/Share					e
// P/E Ratio						r
// Short Ratio						s7
// Dividend Pay Date				r1
// Ex-Dividend Date					q
// Dividend/Share					d
// Dividend Yield					y
// Float Shares						f6
// Market Capitalization			j1
// 1yr Target Price					t8
// EPS Est. Current Yr				e7
// EPS Est. Next Year				e8
// EPS Est. Next Quarter			e9
// Price/EPS Est. Current Yr		r6
// Price/EPS Est. Next Yr			r7
// PEG Ratio						r5
// Book Value						b4
// Price/Book						p6
// Price/Sales						p5
// EBITDA							j4
// 50-day Moving Avg				m3
// Change From 50-day Moving Avg	m7
// Pct Chg From 50-day Moving Av	m8
// 200-day Moving Avg				m4
// Change From 200-day Moving Avg	m5
// Pct Chg From 200-day Moving Avg	m6
// Shares Owned						s1
// Price Paid						p1
// Commission						c3
// Holdings Value					v1
// Day's Value Change				w1,
// Holdings Gain Percent			g1
// Holdings Gain					g4
// Trade Date						d2
// Annualized Gain					g3
// High Limit						l2
// Low Limit						l3
// Notes							n4
// Last Trade (Real-time) with Time	k1
// Bid (Real-time)					b3
// Ask (Real-time)					b2
// Change Percent (Real-time)		k2
// Change (Real-time)				c6
// Holdings Value (Real-time)		v7
// Day's Value Change (Real-time)	w4
// Holdings Gain Pct (Real-time)	g5
// Holdings Gain (Real-time)		g6
// Day's Range (Real-time)			m2
// Market Cap (Real-time)			j3
// P/E (Real-time)					r2
// After Hours Change (Real-time)	c8
// Order Book (Real-time)			i5
// Stock Exchange					x
// *****************************************************************************//

//include files
require_once 'class_general.inc';

//<-- begin class -->
class class_yahoo_quote {
	var $class_name = __CLASS__;	// class name
	var $timeoffset;				//from yahoo servers; GMT
	var $arr_headers 	= array(); 	// array to store quote value headers
	var $QURLbase 		= 'http://download.finance.yahoo.com/d/quotes.csvr?e=.csv&f=';
	var $QURLdefault 	= 'snl1d1t1c1p2va2pomweryj1x';
	var $QURLextended 	= 's7t8e7e8e9r6r7r5b4p6p5j4m3m4';
	var $QURLrealtime 	= 'b2b3k2k1c6m2j3';
	var $QURLend 		= '&s=';
	var $QURL;						// QURL format

	//************* class constructor *************//
	// use $mode to change URL format 
	// 1 = default, 2 = extended, 3 = realtime, 4 = user defined
	// currently, only $mode = 1 is fully supported
	function class_yahoo_quote ($mode = 1, $QURLuserdef = NULL) {
		$QURLformat = $this->QURLdefault;
		$this->timeoffset = class_general::get_timeoffset();
		
		$this->arr_headers = array('ticker', 'security_name', 'price', 'trade_date', 'trade_time', 'change', 'per_change', 'volume', 'ave_volume', 'prev_close', 'open', 'eps', 'pe', 'yield', 'market_cap', 'exchange');

		switch ($mode) {
			case 1:
				break;
				
			case 2:
				$QURLformat .= $this->QURLextended;
				$arr_extraheaders = array('Short Ratio','1yr Target Price','24 EPS Est. Current Yr','EPS Est. Next Y','EPS Est. Next Q','Price/EPS Est. Current Y','Price/EPS Est. Next Y','PEG Ratio','Book Value','Price/Book','Price/Sales','EBITDA','50-day Moving Avg','200-day Moving Avg'); 
				$this->arr_headers = array_merge($this->arr_headers, $arr_extraheaders);
				break;

			case 3:
				$QURLformat .= $this->QURLrealtime;
				$arr_extraheaders = array('Ask (real-time)','Bid (real-time)','% Change (real-time)','Last trade with time (real-time)','Change (real-time)','Day range (real-time)','Market-cap (real-time)');
				$this->arr_headers = array_merge($this->arr_headers, $arr_extraheaders);
				break;

			case 4:
				if ($QURLuserdef) $QURLformat = $QURLuserdef;
				else {
					fwrite(STDERR, "Error in $this->class_name: empty value passed to ".__FUNCTION__);
					fwrite(STDERR, " at line ".__LINE__.".\n");
					return FALSE;
				}

			default:
				fwrite(STDERR, "Error in $this->class_name performing ".__FUNCTION__." at line ");
				fwrite(STDERR, __LINE__." : Please enter a method value of 1, 2, 3 or 4.\n");
				return FALSE;
		} //<-- end switch -->
		
		$arr_endheaders = array('md5','day_low','day_high','w52_low','w52_high');
		$this->arr_headers = array_merge($this->arr_headers, $arr_endheaders);
		$this->QURL = $this->QURLbase.$QURLformat.$this->QURLend;
		fwrite(STDOUT, "$this->class_name class constructor set.\n");
		return TRUE;
	} //<-- end function -->

	//************* gets yahoo quote for a specified ticker *************//
	function get_quote($ticker) {
		$arr_formated_quote = array();
		$raw_quote 			= fopen($this->QURL.$ticker, 'r');
		$quote 				= str_replace('"', '', trim(fread($raw_quote, 2000)));
		fclose($raw_quote);
		$md5 				= md5($quote); // take md5 hash to be used as unique identifier
		$arr_quote 			= explode(",", $quote); // convert quote to an array
		
		// remove instances of 'N/A'
		foreach ($arr_quote as $value) $arr_formated_quote[] = str_replace('N/A', '', $value);
		$arr_quote = $arr_formated_quote;

		// Convert yahoo's date and time to standard format
		$datetime = strtotime($arr_quote[3].$arr_quote[4]);
		$arr_quote[3] = date("m/d/Y", $datetime); // set date mm/dd/yyyy
		$arr_quote[4] = date("H:i", $datetime); // set time to 24hr hh:mm
		
		if ($arr_quote[2] == "0.00" && $arr_quote[3] == "01/01/1970") {
			fwrite(STDERR, "Error in $this->class_name performing ".__FUNCTION__." at line ");
			fwrite(STDERR, __LINE__." : $ticker is not a valid ticker.\n");
			return NULL;
		} //<-- end if -->
		
		// remove instances of '+'
		$arr_quote[5] = str_replace('+', '', $arr_quote[5]);
		$arr_quote[6] = str_replace('+', '', $arr_quote[6]);
		
		$arr_quote[6] = str_replace('%', '', $arr_quote[6]); // remove instances of '%'
		$arr_quote[6] = $arr_quote[6] / 100; // convert percent to decimal
		$arr_quote[15] = $arr_quote[15] / 100; // convert percent to decimal
		
		if (stripos($arr_quote[16],'M')) { // convert from 'M' to millions
			$arr_quote[16] = str_replace('M', '', $arr_quote[16]);
		}
		
		if (stripos($arr_quote[16],'B')) { // convert from 'B' to billions
			$arr_quote[16] = str_replace('B', '', $arr_quote[16]);
			$arr_quote[16] = $arr_quote[16] * 10e3;
		}

		if (stripos($arr_quote[16],'T')) { // convert from from 'T' to trillions
			$arr_quote[16] = str_replace('T', '', $arr_quote[16]);
			$arr_quote[16] = $arr_quote[16] * 10e6;
		}
		
		// if 'range' cells contain no numerical data, delete the '-' 
		if (trim($arr_quote[11]) == '-') $arr_quote[11] = '';
		if (trim($arr_quote[12]) == '-') $arr_quote[12] = '';
		
		$day_low = class_general::extract_part(array($arr_quote[11]), '-', 0);
		$day_high = class_general::extract_part(array($arr_quote[11]), '-', 1);
		$w52_low = class_general::extract_part(array($arr_quote[12]), '-', 0);
		$w52_high = class_general::extract_part(array($arr_quote[12]), '-', 1);
		
		// add new entries
		$arr_quote[] = $md5;
		$arr_quote[] = trim($day_low[0]);
		$arr_quote[] = trim($day_high[0]);
		$arr_quote[] = trim($w52_low[0]);
		$arr_quote[] = trim($w52_high[0]);

		// delete 'range' cells since we no longer need them
		array_splice($arr_quote, 11, 2);
		
		if ($this->arr_headers) $arr_quote = array_combine($this->arr_headers,$arr_quote);
		return $arr_quote;
	} //<-- end function -->
	
	//************* gets yahoo quote for an array of tickers in multiple requests *************//
	function get_multiple_quotes($arr_tickers) {
		foreach ($arr_tickers as $ticker) $arr_quote[] = $this->get_quote($ticker);
		return $arr_quote;
	} //<-- end function -->
	
	//************* gets yahoo quote for an array of tickers in one request *************//
	function get_multiple_quotes_eff($arr_tickers) {
		//my @symbols	= @{(shift)};
		//my $format	= shift;
		//my @qr;
	
		// Loop over the list of symbols, 199 at a time since yahoo only lets you get 200 per request
		//while ($#symbols > -1) {
		//	my @b = $#symbols >= 199 ? splice(@symbols,0,199) 
		//		: splice(@symbols,0,$#symbols+1);
	
		//	my $url = "$QURLbase${format}$QURLend".join('+',@b);
		//	foreach (split('\015?\012',$ua->request(GET $url)->content)) {
		//		my @q = quotewords(',',0,$_);
		//		push(@qr,[@q]);
		//	} //<-- end foreach -->
		//} //<-- end while loop -->
	
		//return \@qr;
	} //<-- end function -->
} //<-- end class -->
?>