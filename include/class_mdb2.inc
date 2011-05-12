<?php
//*****************************************************************************
// purpose: provides an interface to manipulate MDB2 databases 
//*****************************************************************************

// Configuration
$projects_dir		= dirname(dirname(dirname(__FILE__)));

// include files
require_once $projects_dir.'/library/class_general.inc';
require_once 'MDB2.php';

//<-- begin class -->
class class_mdb2 {
	var $arr_tables = array();		// array of table names
	var $arr_databases = array();	// array of database names
	var $definition;				// MDB2 definition array
	var $mdb2;						// MDB2 object
	var $verbose;					// verbose output
	var $class_name = __CLASS__;	// class name
			
	//************* class constructor *************
	function class_mdb2($database_name, $database_type = '', $verbose = FALSE, $database_user = '', $database_password = '', $database_host = '', $database_port = '') {
		$this->verbose						= $verbose;
		if($database_user) $database_user 	= $database_user.':';
		if($database_port) $database_port 	= ':'.$database_port;
		if($database_name) $database_name	= '/'.$database_name;
		
		$dsn = $database_type.'://'.$database_user.$database_password.'@'.$database_host.$database_port.$database_name;
		if($this->verbose) fwrite(STDOUT, "connecting to $dsn\n");
		$this->mdb2 =& MDB2::factory($dsn);
		
		// error check
		if(!PEAR::isError($this->mdb2)) {
			if($this->verbose) fwrite(STDOUT, "$this->class_name class constructor set.\n");
			$this->mdb2->loadModule('Manager');
			return TRUE;
		} else {
			$message = $this->mdb2->getMessage();
			return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 0, 1, $message);
		} //<-- end if -->
	} //<-- end function -->
	
	//************* creates a database *************				
	function create_db($database_name) {
		if(!empty($database_name)) {
			$res = $this->mdb2->createDatabase($database_name); 
		} else return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 1, 1);
		
   	 	if(!PEAR::isError($res)) {
			if($this->verbose) fwrite(STDOUT, "database $database_name created!\n");			
			$this->mdb2->setDatabase($database_name);
			return $res;
		} else {
			$message = $res->getMessage();
			return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 0, 1, $message);
		} //<-- end if -->
	} //<-- end function -->
	
	//************* creates a table *************
	// $definition = array( 
	// 	'id' => array('type' => 'integer', 'unsigned' => 1, 'notnull' => 1, 'default' => 0), 
	// 	'name' => array('type' => 'text', 'length' => 255), 
	// 	'datetime' => array('type' => 'timestamp') 
	// ); 
				
	function create_table($table_name, $tbl_definition, $table_options = NULL) {
		if(!empty($table_name)) {
			$res = $this->mdb2->createTable($table_name, $tbl_definition, $table_options);
		} else return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 1, 1);
		
   	 	if(!PEAR::isError($res)) {
			if($this->verbose) fwrite(STDOUT, "table $table_name created!\n");			
			return $res;
		} else {
			$message = $res->getMessage();
			return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 0, 1, $message);
		} //<-- end if -->
	} //<-- end function -->

	//************* creates a constraint *************
	// primary key
	// $definition = array('primary' => true, 'fields' => array('id' => array()));
	
	// unique constraint
	// $definition = array('unique' => true, 'fields' => array('fieldname' => array()));
	 
	// foreign constraint
	// $definition = array(
	// 	'primary' => false, 
	// 	'unique' => false, 
	// 	'foreign' => true, 
	// 	'check' => false, 
	// 	'fields' => array('field1name' => array('sorting' => ascending|descending, 'position' => 1)), 
	// 	'references' => array(
	// 		'table' => name, 'fields' => array('field1name' => array('position' => 1)) 
	// 		'deferrable' => false, 
	// 		'initiallydeferred' => false, 
	// 		'onupdate' => CASCADE|RESTRICT|SET NULL|SET DEFAULT|NO ACTION, 
	// 		'ondelete' => CASCADE|RESTRICT|SET NULL|SET DEFAULT|NO ACTION, 
	// 		'match' => SIMPLE|PARTIAL|FULL 
	// 	);  
				
	function create_constraint($table_name, $constraint_name, $constraint_definition) {
		if(!empty($table_name)) {
			$res = $this->mdb2->createConstraint($table_name, $constraint_name, $constraint_definition);
		} else return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 1, 1);
		
   	 	if(!PEAR::isError($res)) {
			if($this->verbose) fwrite(STDOUT, "constraint $constraint_name created!\n");			
			return $res;
		} else {
			$message = $res->getMessage();
			return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 0, 1, $message);
		} //<-- end if -->
	} //<-- end function -->
	
	//************* creates a sequence *************				
	function create_sequence($field_name, $start_value = 1) {
		if(!empty($field_name)) {
			$res = $this->mdb2->createSequence($field_name, $start_value); 
		} else return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 1, 1);
		
   	 	if(!PEAR::isError($res)) {
			if($this->verbose) fwrite(STDOUT, "sequence created for $field_name!\n");			
			return $res;
		} else {
			$message = $res->getMessage();
			return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 0, 1, $message);
		} //<-- end if -->
	} //<-- end function -->
	
	//************* creates a database from a converted definition array *************
	function def_arr_to_db($new_definition, $database_name = NULL) {
		if(!empty($new_definition)) {
			if(!$database_name) $database_name = $new_definition['database'];
			$res = $this->create_db($database_name);
			$arr_tables = array_keys($new_definition['tables']);
			$i = 0;
			
			foreach($new_definition['tables'] as $tbl_definition) {
				$table_name = $arr_tables[$i];
				$res = $this->create_table($table_name, $tbl_definition);
				$i++;
			} //<-- end foreach -->
			
			//$res = $this->create_sequence($field_name, $start_value);
			//$res = $this->create_constraint($table_name, $constraint_name, $constraint_definition);
			
			if($this->verbose) fwrite(STDOUT, "$database_name definition array converted to database!\n");			
			return $new_definition;
		} else return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 1, 1);
	} //<-- end function -->
	
	//************* converts a definition array created by MDB2_Schema *************				
	function convert_def_arr($old_definition) {
		if(!empty($old_definition)) {
			$new_definition = array('database' => $old_definition['name']);
			
			foreach($old_definition['tables'] as $table) {
				foreach($table['fields'] as $field) {
					$new_definition['tables'][$table['was']][$field['was']]['type'] = $field['type'];
					$new_definition['tables'][$table['was']][$field['was']]['unsigned'] = $field['unsigned'];
					$new_definition['tables'][$table['was']][$field['was']]['notnull'] = $field['notnull'];
					$new_definition['tables'][$table['was']][$field['was']]['default'] = $field['default'];
					$new_definition['tables'][$table['was']][$field['was']]['length'] = $field['length'];
					if($field['autoincrement'] == 1) $new_definition['sequences'][$table['was']][] = $field['was'];
				} //<-- end foreach -->
			} //<-- end foreach -->

			//if($this->verbose) fwrite(STDOUT, "$old_definition['name'] database definition created!\n");
			return $new_definition;
		} else return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 1, 1);
	} //<-- end function -->
	
	//************* checks for table existance *************
	function check_table_exists($table, $database = NULL) {
		if(empty($this->arr_tables)) $this->arr_tables = $this->mdb2->listTables($database); // check to make sure array is empty
		if(in_array($table, $this->arr_tables)) {
			if($this->verbose) fwrite(STDOUT, "Table $table exists!\n");
			return TRUE;
		} else return FALSE;
	} //<-- end function -->

	//************* checks for database existance *************
	function check_database_exists($database) {
		if(empty($this->arr_databases)) $this->arr_databases = $this->mdb2->listDatabases(); // check to make sure array is empty
		if(in_array($database, $this->arr_databases)) {
			if($this->verbose) fwrite(STDOUT, "Database $database exists!\n");
			return TRUE;
		} else return FALSE;
	} //<-- end function -->
} //<-- end class -->
?>