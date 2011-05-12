<?php
//*****************************************************************************
// purpose: provides an interface to manipulate MDB2 xml schema files 
//*****************************************************************************

// Configuration
$projects_dir		= dirname(dirname(dirname(__FILE__)));

// include files
require_once $projects_dir.'/library/class_general.inc';
require_once 'MDB2/Schema.php';

//<-- begin class -->
class class_mdb2_schema {
	var $definition;					// MDB2 definition array
	var $schema;						// MDB2 schema
	var $verbose;
	var $arr_options = array();
	var $class_name = __CLASS__;		// class name
			
	//************* class constructor *************
	function class_mdb2_schema($database_name, $database_type = '', $verbose = FALSE, $database_user = '', $database_password = '', $database_host = '', $database_port = '', $log_line_break = '<br>', $idxname_format = '%s', $debug = TRUE, $quote_identifier = TRUE, $force_defaults = FALSE, $portability = FALSE) {
		if (!empty($database_name)) {
			$this->arr_options = array(
			    'log_line_break' 	=> $log_line_break,
			    'idxname_format' 	=> $idxname_format,
			    'debug' 			=> $debug,
			    'quote_identifier' 	=> $quote_identifier,
			    'force_defaults' 	=> $force_defaults,
			    'portability' 		=> $portability
			);
			
			$this->verbose						= $verbose;
			if($database_user) $database_user 	= $database_user.':';
			if($database_port) $database_port 	= ':'.$database_port;
			if($database_name) $database_name	= '/'.$database_name;
			
			$dsn = $database_type.'://'.$database_user.$database_password.'@'.$database_host.$database_port.$database_name;
			if($this->verbose) fwrite(STDOUT, "connecting to $dsn\n");
			
		} else return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 1, 1);
		
		$this->schema =& MDB2_Schema::factory($dsn, $this->arr_options);
		
		// error check
		if(!PEAR::isError($this->schema)) {
			if($this->verbose) fwrite(STDOUT, "$this->class_name class constructor set.\n");
			return TRUE;
		} else {
			$message = $this->schema->getMessage();
			return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 0, 1, $message);
		} //<-- end if -->
	} //<-- end function -->
	
	//************* creates an MDB2 definition array from an existing database *************
	function db_to_def_arr() {
		$this->definition = $this->schema->getDefinitionFromDatabase();
		
		if(!PEAR::isError($this->definition)) {
			if($this->verbose) {
				$def_arr_name = $this->definition['name'];
				fwrite(STDOUT, "MDB2 definition array $def_arr_name created!\n");
			} //<-- end if -->
			
			return $this->definition;
		} else {
			$message = $this->definition->getMessage();
			return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 0, 1, $message);
		} //<-- end if -->
	} //<-- end function -->
	
	//************* creates an MDB2 definition array from an XML schema file *************
	function xml_to_def_arr($schema_file) {
		if(file_exists($schema_file)) {
			$this->definition = $this->schema->parseDatabaseDefinitionFile($schema_file);
			
			if(!PEAR::isError($this->definition)) {
				if($this->verbose) {
					$def_arr_name = $this->definition['name'];
					fwrite(STDOUT, "MDB2 definition array $def_arr_name created!\n");
				} //<-- end if -->
					
				return $this->definition;
			} else {
				$message = $this->definition->getMessage();
				return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 0, 1, $message);
			} //<-- end if -->
		} else return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 3, 2, $schema_file);
	} //<-- end function -->
	
	//************* creates an XML schema file from an existing database *************
	// $dump_mode 
	// 1 = the entire db, 2 = only the db structure, 3 = only the db content
	function db_to_xml($schema_file, $dump_mode = 1) {
		$arr_options = array(
	      'output_mode' => 'file',
	      'output' => $schema_file,
	      'end_of_line' => "\n"
	    );
	    
	    $schema_file_name = class_general::get_filename($schema_file);
	    
		// switch to select the appropriate case function
		switch ($dump_mode) {
			case 1:
				$dump_type = MDB2_SCHEMA_DUMP_ALL;
				break;
			case 2:
				$dump_type = MDB2_SCHEMA_DUMP_STRUCTURE;
				break;
			case 3:
				$dump_type = MDB2_SCHEMA_DUMP_CONTENT;
				break;
			default:
				return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 4, 2);
		} //<-- end switch -->

	    $check = $this->db_to_def_arr();

	    if($check) {
	    	$res = $this->schema->dumpDatabase($this->definition, $arr_options, $dump_type);
	    	if(PEAR::isError($res)) $errors = TRUE;
	    } else $errors = TRUE;	
	    
	    if(!$errors) {
			if($this->verbose) fwrite(STDOUT, "schema file $schema_file_name created!\n");
			return $res;
		} else {
			if($res) {
				$message = $res->getMessage();
				return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 0, 1, $message);
			} else return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 6, 1);
		} //<-- end if -->			
	} //<-- end function -->
} //<-- end class -->
?>