#!/usr/bin/php
<?php
// Configuration
$project_loc	= dirname(__FILE__);
$parent_dir		= dirname($project_loc);
$select_dir 	= $project_loc.'/out_files';
$def_ext 		= 'out';
$join_dir 		= $project_loc.'/join_files';
	
// include files
require_once 'Console/CommandLine.php';
require_once $parent_dir.'/library/error2.inc';
require_once $project_loc.'/include/class_pgsql.inc';

// create the parser from xml file
$xmlfile = $project_loc.'/dbselect.xml';
$parser = Console_CommandLine::fromXmlFile($xmlfile);

// run the parser
try {
	$result = $parser->parse();

	//*************************************
	// Begin get
	//*************************************

	// main command argument
	$database_name 			= $result->args['database'];
	
	// subcommand arguments
	$needle_table 			= $result->command->args['needle_table'];
	$haystack_table 		= $result->command->args['haystack_table'];
	$column_w_keys 			= $result->command->args['column_w_keys'];
	$arr_needle_columns		= $result->command->args['needle_columns'];
	$replacement_column 	= $result->command->args['replacement_column'];
	
	// load main options if present
	if ($result->options['output_dir']) $select_dir = $result->options['output_dir'];
	if ($result->options['join_dir']) $join_dir = $result->options['join_dir'];
	
	// set subcommand option defaults
	if (!$result->options['dest_table']) $result->options['dest_table'] = $result->command->args['needle_table'];
	
	switch ($result->command_name) {
		case 'matched':
			if (!$result->command->options['needle_column']) {
				$result->command->options['needle_column'] = $result->command->args['haystack_table'];
			}
		
			if (!$result->command->options['needle_column2']) {
				$result->command->options['needle_column2'] = $result->command->args['haystack_table'];
			}

			break;
			
		case 'unmatched':
			if (!$result->command->options['needle_column']) {
				$result->command->options['needle_column'] = $result->command->args['needle_table'];
			}
		
			if (!$result->command->options['needle_column2']) {
				$result->command->options['needle_column2'] = $result->command->args['needle_table'];
			}
			
			if (!$result->command->options['keys']) {
				$result->command->options['keys'] = $result->command->args['needle_table'];
			}
			
		} //<-- end switch -->			
	
	// main command options
	$debugmode			= $result->options['debug'];
	$varmode			= $result->options['variable'];
	$testmode			= $result->options['test'];
	$joinmode			= $result->options['join'];
	$file_base			= $result->options['file_base'];
	$dest_table			= $result->options['dest_table'];
	
	// subcommand options
	$copies				 = $result->command->options['copies'];
	$needle_column		 = $result->command->options['needle_column'];
	$needle_column2		 = $result->command->options['needle_column2'];
	$keys	 			 = $result->command->options['keys'];
	if ($keys) $arr_keys = explode(',',$keys); // convert string to array
	
	// program setting
	$general = new class_general();	
	$program = $general->get_base(__FILE__);
	
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
	$connection = new class_pgsql($database_name);

	switch ($result->command_name) {
		case 'regular':
			$arr_results = $connection->select_regular($needle_table, $arr_needle_columns, $column_w_keys);
			break;
			
		case 'matched':
			$arr_results = $connection->select_matched($haystack_table, $needle_table, $needle_column, $needle_column2, $column_w_keys, $replacement_column);
			break;
			
		case 'unmatched':
			$arr_results = $connection->select_unmatched($haystack_table, $needle_table, $needle_column, $needle_column2, $copies);
	} //<-- end switch -->
	
	if (!empty($arr_results)) {
		if (!$joinmode) {
			if (!is_array(current($arr_results))) $arr_results = array($arr_results); // patch for array2string if there is only one row
			$arr_results = $general->array2string($arr_results, $arr_keys); // convert array to a more simplified form
			$general->error_check($arr_results, $program);
			
			if (!$testmode) {
				$serial_results = serialize($arr_results); // save data in format that can be written to file
				$filenum = $general->countfiles($select_dir, $def_ext) + 1;
				$outfile = $select_dir.'/'.$dest_table.'['.$filenum.'].'.$def_ext;
				$check = $general->write2file($serial_results, $outfile); // write data to file
				$general->error_check($check, $program);
			
			} else {
				print_r($arr_results);
				print("\n"); 
			} //<-- end if -->
			
		} elseif (!$testmode) {		
			$serial_results = serialize($arr_results); // save data in format that can be written to file
			$size = strlen($serial_results);
			$filenum = $general->countfiles($join_dir) + 1;
			$joinfile = $join_dir.'/'.$size.'.'.$filenum;
			$check = $general->write2file($serial_results, $joinfile); // write data to file
			$general->error_check($check, $program);
			
		} else print_r($arr_results);
	
		fwrite(STDOUT, "Program $program completed successfully!\n");
		exit(0);
		
	} else {
		fwrite(STDOUT, "Program $program completed: no data to write out.\n");
		exit(0);
	} //<-- end if -->
	
	//*************************************
	// End get 
	//*************************************
} catch (Exception $exc) {
	$parser->displayError($exc->getMessage());
}
?>