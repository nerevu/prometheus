#!/usr/bin/php
<?php
// Configuration
$thisproject_dir	= dirname(__FILE__);
$projects_dir		= dirname($thisproject_dir);
$schema_path		= $thisproject_dir.'/schema_files/';
$source_db_type		= 'sqlite';
$source_db_user		= trim(shell_exec('whoami'));
$source_db_pwd 		= '';
$source_db_host		= 'localhost';
$source_db_port		= '';
$dest_db_type		= 'pgsql';
$dest_db_user		= '';
$dest_db_pwd 		= '';
$dest_db_host		= '';
$dest_db_port		= '';
$check 				= false;

// include files
require_once 'Console/CommandLine.php';
require_once $projects_dir.'/library/error2.inc';
require_once $projects_dir.'/library/class_general.inc';
require_once $thisproject_dir.'/include/class_mdb2_schema.inc';
require_once $thisproject_dir.'/include/class_mdb2.inc';

// create the parser from xml file
$xmlfile = $thisproject_dir.'/sqlite2pgsql.xml';
$parser = Console_CommandLine::fromXmlFile($xmlfile);

// run the parser
try {
	$result = $parser->parse();

	//*************************************
	// Begin sqlite2pgsql
	//*************************************

	// program setting
	$general = new class_general($verbose);
	$program = $general->get_base(__FILE__);
	
	// command argument
	$source_db_name 	= $general->get_base($result->args['source_db_name']);

	// load options if present
	if(!$result->options['dest_db_name']) $dest_db_name = $source_db_name;
	else $dest_db_name = $result->options['dest_db_name'];
	
	if(!$result->options['schema_file']) $schema_file = $schema_path.$source_db_name.'.xml';
	else $schema_file = $result->options['schema_file'];
	
	if($result->options['source_db_type']) $source_db_type = $result->options['source_db_type'];
	if($result->options['source_db_user']) $source_db_user = $result->options['source_db_user'];
	if($result->options['source_db_pwd']) $source_db_pwd = $result->options['source_db_pwd'];
	if($result->options['source_db_host']) $source_db_host = $result->options['source_db_host'];
	if($result->options['source_db_port']) $source_db_port = $result->options['source_db_port'];
	if($result->options['dest_db_type']) $dest_db_type = $result->options['dest_db_type'];
	
	if(!$result->options['dest_db_user']) $dest_db_user = $source_db_user;
	else $dest_db_user = $result->options['dest_db_user'];
	
	if(!$result->options['dest_db_pwd']) $dest_db_pwd = $source_db_pwd;
	else $dest_db_pwd = $result->options['dest_db_pwd'];
	
	if(!$result->options['dest_db_host']) $dest_db_host = $source_db_host;
	else $dest_db_host = $result->options['dest_db_host'];
	
	if(!$result->options['dest_db_port']) $dest_db_port = $source_db_port;
	else $dest_db_port = $result->options['dest_db_port'];
	
	// command options
	$debugmode	= $result->options['debug'];
	$varmode	= $result->options['variables'];
	$verbose	= $result->options['verbose'];

	// debug and variable mode settings
	if($debugmode OR $varmode) {
		if($debugmode) {
			print("[Command opts] ");
			print_r($result->options);
			print("[Command args] ");
			print_r($result->args);
		} //<-- end if -->

		if($varmode) $general->print_vars(get_defined_vars());
		exit(0);
	} //<-- end if -->

	// execute program
	$connection = new class_mdb2_schema($source_db_name, $source_db_type, $verbose, $source_db_user, $source_db_pwd, $source_db_host, $source_db_port);
	
	if($connection) {
		//$check = $connection->db_to_xml($schema_file);
		$check = true;
		if($check) {
			//$connection = new class_mdb2($dest_db_name, $dest_db_type, $verbose, $dest_db_user, $dest_db_pwd, $dest_db_host, $dest_db_port);
			if($connection) {
				//$old_definition = $connection->db_to_def_arr();
				$old_definition = $connection->xml_to_def_arr($schema_file);
				$connection = new class_mdb2($source_db_name, $source_db_type, $verbose, $source_db_user, $source_db_pwd, $source_db_host, $source_db_port);
				$new_definition = $connection->convert_def_arr($old_definition);
				//print_r($new_definition);
				$connection->def_arr_to_db($new_definition);
				
				if(!$check) $errors = TRUE;
			} else $errors = TRUE;	
		} else $errors = TRUE;
	} else $errors = TRUE;

	if(!$errors) {
		if($verbose) fwrite(STDOUT, "Program $program completed successfully!\n");
		exit(0);
	} else {
		fwrite(STDERR, "Program $program completed with errors.\n");
		exit(1);
	} //<-- end if errors -->
	
	//*************************************
	// End sqlite2pgsql 
	//*************************************
} catch (Exception $exc) {
	$parser->displayError($exc->getMessage());
}
?>