#!/usr/bin/php
<?php
// Configuration
$project_loc	= dirname(__FILE__);
$parent_dir		= dirname($project_loc);
$output_dir 	= $project_loc.'/out_files';
$out_ext 		= 'out';
$needle_table	= 'security';
$out_table		= 'security_updates';
$key			= NULL;
$arr_columns	= array('ticker');
$where_column	= 'is_quotable';
$where_value	= 'TRUE';

// include files
require_once 'Console/CommandLine.php';
require_once $parent_dir.'/library/error2.inc';;
require_once $project_loc.'/include/class_pgsql.inc';
require_once $project_loc.'/include/class_yahoo_quote.inc';

// create the parser from xml file
$xmlfile = $project_loc.'/getquote.xml';
$parser = Console_CommandLine::fromXmlFile($xmlfile);

// run the parser
try {
	$result = $parser->parse();

	//*************************************
	// Begin getquoute
	//*************************************
	
	// command argument
	$database_name 		= $result->args['database'];
	
	// load options if present
	if ($result->options['output_dir']) $output_dir = $result->options['output_dir'];
	
	// set option defaults
	if (!$result->options['needle_table']) $result->options['needle_table'] = $needle_table;
	
	// command options
	$debugmode			= $result->options['debug'];
	$varmode			= $result->options['variable'];
	$testmode			= $result->options['test'];
	
	// program setting
	$general = new class_general();
	$program = $general->get_base(__FILE__);
	
	// debug and variable mode settings
	if ($debugmode OR $varmode) {
		if ($debugmode) {
			print("[Command opts] ");
			print_r($result->options);
			print("[Command args] ");
			print_r($result->args);
		} //<-- end if -->

		if ($varmode) $general->print_vars(get_defined_vars());
		exit(0);
	} //<-- end if -->
	
	// execute program
	$connection = new class_pgsql($database_name);
	$yahoo_quote = new class_yahoo_quote();
	
	$arr_tickers = $connection->select_regular($needle_table, $arr_columns, $key, $where_column, $where_value);
	$general->error_check($arr_tickers, $program);
	$arr_tickers = $general->array2string($arr_tickers); // compress 'array of array' to an array
	$general->error_check($arr_tickers, $program);
	array_shift($arr_tickers); // remove first entry of array
	//$arr_quotes = $yahoo_quote->get_quote('ibm');
	//$arr_quotes = $yahoo_quote->get_multiple_quotes(array('IBM','MRK'));
	$arr_quotes = $yahoo_quote->get_multiple_quotes($arr_tickers);
	
	if (!empty($arr_quotes)) {
		if (!is_array(current($arr_quotes))) $arr_quotes = array($arr_quotes); // patch for array2string if there is only one ticker
		$arr_quotes = $general->array2string($arr_quotes); // convert array to a more simplified form
		$general->error_check($arr_quotes, $program);
		
		if (!$testmode) {
			$serial_values = serialize($arr_quotes); // save data in format that can be written to file
			$filenum = $general->countfiles($output_dir, $out_ext) + 1;
			$outfile = $output_dir.'/'.$out_table.'['.$filenum.'].'.$out_ext;
			$check = $general->write2file($serial_values, $outfile); // write data to file
			$general->error_check($check, $program);
		
		} else {
			print_r($arr_quotes);
			print("\n"); 
		} //<-- end if -->
	
		fwrite(STDOUT, "Program $program completed successfully!\n");
		exit(0);
		
	} else {
		fwrite(STDOUT, "Program $program completed: no data to write out.\n");
		exit(0);
	} //<-- end if -->
				
	//*************************************
	// End getquoute 
	//*************************************
} catch (Exception $exc) {
	$parser->displayError($exc->getMessage());
}
?>