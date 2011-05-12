#!/usr/bin/php
<?php
// Configuration
$project_loc	= dirname(__FILE__);
$select_dir 	= $project_loc.'/out_files';
$def_ext 		= 'out';
$join_dir 		= $project_loc.'/join_files';
$joined_dir		= $join_dir.'/completed';
$parent_dir		= dirname($project_loc);

// include files
require_once 'Console/CommandLine.php';
require_once $parent_dir.'/library/error2.inc';
require_once $parent_dir.'/library/class_general.inc';


// create the parser from xml file
$xmlfile = $project_loc.'/join-files.xml';
$parser = Console_CommandLine::fromXmlFile($xmlfile);

// run the parser
try {
	$result = $parser->parse();

	//*************************************
	// Begin join-files
	//*************************************
	
	// command argument
	$dest_table			= $result->args['dest_table'];
	
	// load options if present
	if ($result->options['output_dir']) $select_dir = $result->options['output_dir'];
	if ($result->options['join_dir']) $join_dir = $result->options['join_dir'];
	
	// command options
	$debugmode			= $result->options['debug'];
	$varmode			= $result->options['variable'];
	$testmode			= $result->options['test'];
	$append 			= $result->options['append'];
	if ($append) $arr_append = explode(',',$append); // convert string to array
	$keys 				= $result->options['keys'];
	if ($keys) $arr_keys = explode(',',$keys); // convert string to array
	
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
	if ($arr_filenames = $general->get_filenames($join_dir)) {
		//usort($arr_filenames, array('class_general', 'cmpByLength'));
		rsort($arr_filenames, SORT_NUMERIC);
		$arr_files = $general->filename2file($arr_filenames, $join_dir);
		$arr_arrays = $general->unserialize_batch($arr_files);
		$arr_joined = $general->array_compress($arr_arrays);
		$general->error_check($arr_joined, $program);
		
		if ($arr_append) {
			$arr_joined = $general->array_append($arr_joined, $arr_append);
			$general->error_check($arr_joined, $program);
		} //<-- end if -->
		
		// convert array to a more simplified form
		$arr_joined = $general->array2string($arr_joined, $arr_keys);
		$general->error_check($arr_joined, $program);
		
		if (!$testmode) {
			$serial_joined = serialize($arr_joined); // save data in format that can be written to file
			$filenum = $general->countfiles($select_dir, $def_ext) + 1;
			$outfile = $select_dir.'/'.$dest_table.'['.$filenum.'].'.$def_ext;
			
			$check = $general->write2file($serial_joined, $outfile); // write joined data to file
			$general->error_check($check, $program);
			foreach ($arr_files as $file) if (!$general->move_file($file, $joined_dir)) $errors = TRUE;
	
		} else {
			print("Will create join file: ");
			print_r($arr_joined);
		} //<-- end if testmode -->
			
		if (!$errors) {
			fwrite(STDOUT, "Program $program completed successfully!\n");
			exit(0);
		} else {
			fwrite(STDERR, "Program $program completed with errors.\n");
			exit(1);
		} //<-- end if -->
		
	} else {
		fwrite(STDOUT, "Program $program completed: no files to join.\n");
		exit(0);
	} //<-- end if -->
	//*************************************
	// End join-files 
	//*************************************
} catch (Exception $exc) {
	$parser->displayError($exc->getMessage());
}
?>
		
		
		