#!/usr/bin/php
<?php
// Configuration
$project_loc	= dirname(__FILE__);
$parent_dir		= dirname($project_loc);
$csv_dir	 	= '/Users/reubano/Downloads/csv_files';
$csv_ext 		= 'csv';
$imported_dir	= $csv_dir.'/completed';

// include files
require_once 'Console/CommandLine.php';
require_once $parent_dir.'/library/error2.inc';
require_once $project_loc.'/include/class_pgsql.inc';
require_once $project_loc.'/include/class_csv2postgres.inc';

// create the parser from xml file
$xmlfile = $project_loc.'/insert-csv.xml';
$parser = Console_CommandLine::fromXmlFile($xmlfile);

// run the parser
try {
	$result = $parser->parse();

	//*************************************
	// Begin insert-csv
	//*************************************
	
	// command argument
	$database_name 		= $result->args['database'];

	// load options if present
	if ($result->options['csv_dir']) $csv_dir = $result->options['csv_dir'];
	
	// command options
	$debugmode			= $result->options['debug'];
	$varmode			= $result->options['variable'];
	$testmode			= $result->options['test'];
	$cleartable			= $result->options['clear'];
	$files				= $result->options['files'];
	$header				= $result->options['header'];
	
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
	
	if ($files) $arr_filenames = explode(',', $files);
	else $arr_filenames = $general->get_filenames($csv_dir, $csv_ext);
	
	if ($arr_filenames) {
		$arr_files = $general->filename2file($arr_filenames, $csv_dir);
		$arr_table_names = $general->extract_part($arr_filenames,"[");
	
		if (!$testmode) {
			if ($max_tables = count($arr_table_names)) {;
				$csv2postgres = new class_csv2postgres();	
				
				for ($i=0; $i<$max_tables; $i++) { // import csv into postgres
					$connection->transaction(); // begin transaction
					if ($cleartable) $connection->clear_table($arr_table_names[$i]);
					if ($csv2postgres->import_csv($arr_files[$i], $arr_table_names[$i], $header)) {
						$connection->commit(); // commit transaction
						$general->move_file($arr_files[$i], $imported_dir);
					} else {
						$connection->rollback(); // rollback transaction
						fwrite(STDERR, "Error in program $program at line ".__LINE__);
						fwrite(STDERR, ": could not complete import_csv on $arr_files[$i].\n");
						$errors = TRUE;
					} //<-- end if -->
				} //<-- end for -->
			} //<-- end if -->
			
		} else {
			print("Will insert files: ");
			print_r($arr_filenames);
			print("into tables: ");
			print_r($arr_table_names);
		} //<-- end if -->
		
		if (!$errors) {
			fwrite(STDOUT, "Program $program completed successfully!\n");
			exit(0);
		} else {
			fwrite(STDERR, "Program $program completed with errors.\n");
			exit(1);
		} //<-- end if -->
		
	} else {
		fwrite(STDOUT, "Program $program completed: no files to import.\n");
		exit(0);
	} //<-- end if -->
	
	//*************************************
	// End insert-csv 
	//*************************************
} catch (Exception $exc) {
	$parser->displayError($exc->getMessage());
}
?>
		
		
		