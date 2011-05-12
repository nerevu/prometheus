#!/usr/bin/php
<?php
// Configuration
$project_loc	= dirname(__FILE__);
$parent_dir		= dirname($project_loc);
$select_dir	 	= $project_loc.'/out_files';
$converted_dir	= $select_dir.'/completed';
$def_ext 		= 'out';
$csv_dir	 	= '/Users/reubano/Downloads/csv_files';
$csv_ext 		= 'csv';
	
// include files
require_once 'Console/CommandLine.php';
require_once $parent_dir.'/libary/error2.inc';
require_once $parent_dir.'/libary/class_general.inc';

// create the parser from xml file
$xmlfile = $project_loc.'/create-csv.xml';
$parser = Console_CommandLine::fromXmlFile($xmlfile);

// run the parser
try {
	$result = $parser->parse();

	//*************************************
	// Begin create-csv
	//*************************************
	
	// load options if present
	if ($result->options['input_dir']) $select_dir = $result->options['input_dir'];
	if ($result->options['csv_dir']) $csv_dir = $result->options['csv_dir'];
	
	// command options
	$debugmode			= $result->options['debug'];
	$varmode			= $result->options['variable'];
	$testmode			= $result->options['test'];
	$files				= $result->options['files'];
	
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
	if ($files) $arr_filenames = explode(',', $files);
	else $arr_filenames = $general->get_filenames($select_dir, $def_ext);
	
	if ($arr_filenames) {
		$arr_table_names = $general->extract_part($arr_filenames,"[");
		$arr_files = $general->filename2file($arr_filenames, $select_dir);
		$arr_arrays = $general->unserialize_batch($arr_files);
		
		if (!$testmode) {
			$max_tables = count($arr_table_names);
			
			for ($i=0; $i<$max_tables; $i++) {
				$filenum = $general->countfiles($csv_dir, $csv_ext) + 1;
				$csvfile = $csv_dir.'/'.$arr_table_names[$i].'['.$filenum.'].'.$csv_ext;
				
				if ($general->array2csv($arr_arrays[$i], $csvfile)) { // check to make sure array is converted to csv
					$check = $general->move_file($arr_files[$i], $converted_dir); // check to make sure file is moved
					if (!check) $errors = TRUE;
				} else $errors = TRUE;
			} //<-- end for -->
			
		} else {
			print("Will create csv file: ");
			print_r($arr_arrays);
		} //<-- end if -->
		
		if (!$errors) {
			fwrite(STDOUT, "Program $program completed successfully!\n");
			exit(0);
		} else {
			fwrite(STDERR, "Program $program completed with errors.\n");
			exit(1);
		} //<-- end if -->
		
	} else {
		fwrite(STDOUT, "Program $program completed: no files to create.\n");
		exit(0);
	} //<-- end if -->
				
	//*************************************
	// End create-csv 
	//*************************************
} catch (Exception $exc) {
	$parser->displayError($exc->getMessage());
}
?>