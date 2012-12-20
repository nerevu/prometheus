#!/usr/bin/php
<?php
// General configuration
$project_loc		= dirname(__FILE__);					// project directory
$parent_dir		= dirname($project_loc);					// parent directory
$username			= 'reubano';							// user's computer login name
$select_dir		 	= $project_loc.'/out_files';			// directory for saving output files
$join_dir 			= $project_loc.'/join_files';			// directory for saving files to join
$schema_dir			= $project_loc.'/schema_files';			// directory for saving XML schema files
$joined_dir			= $join_dir.'/completed';				// directory for saving joined files
$converted_dir		= $select_dir.'/completed';				// directory for saving files that have been converted to csv
$csv_dir 			= '/Users/'.$username.'/Downloads/csv_files';	// directory for saving csv files 
$imported_dir		= $csv_dir.'/completed';				// directory for saving files that have been imported into db
$def_ext 			= 'out';								// def extention for output files
$csv_ext 			= 'csv';								// def extention for csv files
$database_name		= 'myportfolio';						// database name
$database_host 		= 'localhost';							// database host
$database_port 		= "";									// database port
$start_date		 	= 'last year';
$end_date		 	= 'today';

// import-trans configuration
$new_trans_file 				= 'transaction_new.csv';
$new_trans_table 				= 'transaction_new';
$new_trans_ticker_column		= 'ticker';
$new_trans_key_column 			= 'tran_id';
$arr_new_trans_select_columns	= array('date', 'price', 'quantity', 'commission', 'amount');
$new_trans_copies 				= 2;
$real_trans_table	 			= 'transaction_real';
$security_table 				= 'security';
$security_table_key_column		= 'security_id';
$action_table	 				= 'action';
$action_table_key_column		= 'action_id';
$arr_new_sec_keys 				= array('security_name', 'ticker');
$arr_new_trans_keys 			= array('import_id', 'tran_date', 'price', 'quantity', 'commission', 'cashflow', 'security_id', 'action_id', 'account_id');

// other
$def_account_id 	= 1;
$new_xray_file 		= 'security_xray_new.csv';
$def_security_id 	= 1;

// other
$needle_table 		= $result;
$haystack_table 	= $result;
$column_w_keys 		= $result;
$arr_needle_columns	= $result;
$replacement_column = $result;
$needle_column		= $result;
$needle_column2		= $result;
$copies				= $result;
	
// include files
require_once 'Console/CommandLine.php';
require_once $parent_dir.'/library/error2.inc';
require_once $project_loc.'/include/class_allocreator.inc';

// create the parser from xml file
$xmlfile = $project_loc.'/allocreator.xml';
$parser = Console_CommandLine::fromXmlFile($xmlfile);

try { //<-- begin parser -->
	$result = $parser->parse();

	//*************************************
	// Begin allocreator
	//*************************************

	// main command options
	$debugmode			= $result->options['debug'];
	$varmode			= $result->options['variable'];
	$testmode			= $result->options['test'];
	
	// set subcommand option
	switch ($result->command_name) {
		case 'update-db':
			// load defaults
			if (!$result->command->options['file']) $result->command->options['file'] = $new_trans_file;
			if (!$result->command->options['account']) $result->command->options['account'] = $def_account_id;
			
			// set vars
			$file = $result->command->options['file'];
			if ($file) $arr_file = array($file);			
			$account = $result->command->options['account'];
			if ($account) $arr_account = array($account);
			break;
			
		case 'import-trans':
			// load defaults
			if (!$result->command->options['file']) $result->command->options['file'] = $new_trans_file;
			if (!$result->command->options['account']) $result->command->options['account'] = $def_account_id;
			
			// set vars
			$file = $result->command->options['file'];
			if ($file) $arr_file = array($file);			
			$account = $result->command->options['account'];
			if ($account) $arr_account = array($account);
			break;
			
		case 'import-xray':
			// load defaults
			if (!$result->command->options['file']) $result->command->options['file'] = $new_xray_file;
			if (!$result->command->options['security']) $result->command->options['security'] = $def_security_id;
			
			// set vars
			$file = $result->command->options['file'];
			if ($file) $arr_file = array($file);
			$security = $result->command->options['security'];
			break;
			
		case 'update':
			// set vars
			$force = $result->command->options['force'];
			$tickers = $result->command->options['tickers'];
			if ($tickers) $arr_tickers = explode(',',$tickers); // convert string to array
			break;
			
		case 'populate':
			// load defaults
			if (!$result->command->options['start']) $result->command->options['start'] = $start_date;
			if (!$result->command->options['end']) $result->command->options['end'] = $end_date;
			
			// set vars
			$start = $result->command->options['start'];
			$end = $result->command->options['end'];
			$force = $result->command->options['force'];
			$tickers = $result->command->options['tickers'];
			if ($tickers) $arr_tickers = explode(',',$tickers); // convert string to array
			break;
			
		case 'quote':
			// load defaults
			if (!$result->command->options['date']) $result->command->options['date'] = $end_date;
			
			// set vars
			$update = $result->command->options['update'];
			$mode = $result->command->options['mode'];
			$tickers = $result->command->options['tickers'];
			if ($tickers) $arr_tickers = explode(',',$tickers); // convert string to array
			break;
			
		case 'list':
			// set vars
			$mode = $result->command->options['mode'];
			$tickers = $result->command->options['tickers'];
			if ($tickers) $arr_tickers = explode(',',$tickers); // convert string to array
			break;
			
		case 'sreport':
			// load defaults
			if (!$result->command->options['date']) $result->command->options['date'] = $end_date;
			
			// set vars
			$date = $result->command->options['date'];
			$update = $result->command->options['update'];
			$mode = $result->command->options['mode'];
			$names = $result->command->options['names'];
			if ($name) $arr_names = explode(',',$names); // convert string to array
			break;
			
		case 'plreport':
			// load defaults
			if (!$result->command->options['start']) $result->command->options['start'] = $start_date;
			if (!$result->command->options['end']) $result->command->options['end'] = $end_date;
			
			// set vars
			$start = $result->command->options['start'];
			$end = $result->command->options['end'];
			$update = $result->command->options['update'];
			$mode = $result->command->options['mode'];
			$range = $result->command->options['range'];
			$names = $result->command->options['names'];
			if ($name) $arr_names = explode(',',$names); // convert string to array
	} //<-- end switch -->		
	
	// program setting
	$general = new class_general();
	$program = $general->get_base(__FILE__);
	$connection = new class_pgsql($database_name);
	
	// debug and variable mode settings
	if ($debugmode OR $varmode) {
		if ($debugmode) {
			print("[Main command opts] ");
			print_r($result->options);
			print("[Main command args] ");
			print_r($result->args);
			print("[Subcommand name] => $result->command_name\n");
			print("[Subcommand opts] ");
			print_r($result->command->options);
			print("[Subcommand args] ");
			print_r($result->command->args);
		} //<-- end if -->

		if ($varmode) $general->print_vars(get_defined_vars());
		
		exit(0);
	} //<-- end if -->
	
	// execute program
	$allocreator = new class_allocreator($database_name, $database_host, $database_port, $project_loc, $select_dir, $join_dir, $joined_dir, $converted_dir, $csv_dir, $imported_dir, $def_ext, $csv_ext);
	$arr_files = array();
	
	// set subcommand option
	switch ($result->command_name) {
		case 'import-trans':
			// import new transactions to [transaction_new]
			$check = $allocreator->import_csvfiles($arr_file, TRUE);
			$general->error_check($check, $program);
			
			// add new securities from [transaction_new] to [security]
			$arr_results = $connection->select_unmatched($new_trans_table, $security_table, $security_table, $new_trans_ticker_column, $new_trans_copies);
			
			if ($arr_results) {
				$arr_files[] = $allocreator->create_outfile($security_table, $arr_results, $arr_new_sec_keys);
				$arr_files = $allocreator->create_csvfiles($arr_files);
				$allocreator->import_csvfiles($arr_files);
				unset($arr_files);
			} else fwrite(STDOUT, "No new securties to add\n");
			return;
			exit(0);

			// add new actions from [transaction_new] to [action]
			$arr_results = $connection->select_unmatched($new_trans_table, $action_table, $action_table, $action_table);

			if ($arr_results) {
				$arr_files[] = $allocreator->create_outfile($action_table, $arr_results);
				$arr_files = $allocreator->create_csvfiles($arr_files);
				$allocreator->import_csvfiles($arr_files);
				unset($arr_files);
			} else fwrite(STDOUT, "No new actions to add\n");

			// add new transactions from [transaction_new] to [transaction_real]
			$arr_results = $connection->select_regular($new_trans_table, $arr_new_trans_select_columns, $new_trans_key_column);
			$arr_files[] = $allocreator->create_joinfile($arr_results);

			$arr_results = $connection->select_matched($security_table, $new_trans_table, $security_table, $new_trans_ticker_column, $new_trans_key_column, $security_table_key_column);
			$arr_files[] = $allocreator->create_joinfile($arr_results);
			
			$arr_results = $connection->select_matched($action_table, $new_trans_table, $action_table, $action_table, $new_trans_key_column, $action_table_key_column);
			$arr_files[] = $allocreator->create_joinfile($arr_results);
			
			$arr_results = $allocreator->joinfiles($real_trans_table, $arr_files, $arr_account);
			unset($arr_files);
			$general->error_check($arr_results, $program);
			
			$arr_files[] = $allocreator->create_outfile($real_trans_table, $arr_results, $arr_new_trans_keys);
			$arr_files = $allocreator->create_csvfiles($arr_files);
			$check = $allocreator->import_csvfiles($arr_files);
			unset($arr_files);
			$general->error_check($check, $program);
			break;
			
		case 'import-xray':
			// import new x-ray to [new_xray]
			// insert-csv -hsec_prop_name,sec_prop_value myportfolio
			// dbselect -i myportfolio regular new_xray sec_xray_id sec_prop_value
			// dbselect -i myportfolio matched -lsec_prop_name -msec_prop_name new_xray sec_xray_id security_property sec_prop_id
			// join-files -ksec_xray_id,sec_prop_value,sec_prop_id,security_id -a46 security_xray
			// create-csv
			// insert-csv myportfolio
			break;
			
		case 'update':
			// import new security info to [security_updates]
			// getquote myportfolio
			// create-csv
			// insert-csv -rf security_updates[1].csv myportfolio
			
			// update security info from [security_updates] to [security]
			break;
			
		case 'populate':
			break;
			
		case 'quote':
			break;
			
		case 'list':
			break;
			
		case 'sreport':
			break;
			
		case 'plreport':
	} //<-- end switch -->
	
	//*************************************
	// End allocreator 
	//*************************************
} catch (Exception $exc) {
	$parser->displayError($exc->getMessage());
} //<-- end parser -->
?>