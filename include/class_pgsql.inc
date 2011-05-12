<?php
//*****************************************************************************
// purpose: contains specfic functions for dealing with Postgres tables 
//*****************************************************************************

//include files
require_once 'class_general.inc';

//<-- begin class -->
class class_pgsql {
	var $class_name 		= __CLASS__;// class name
	var $database_name;					// database name
	var $database_host;					// database host
	var $database_port;					// database port
	var $num_rows;						// number of rows
	var $arr_column_names	= array();	// array of column names
	var $arr_data_types		= array();	// array of data types
	var $arr_tables 		= array();	// array of table names
	var $sql_error; 					// error message
	//var $obj_general;					// object to hold methods from class_general class
	
	//************* class constructor *************
	function class_pgsql($database_name, $database_host = 'localhost', $database_port = "") {
		if (!empty($database_name)) {
			$this->database_name	= $database_name;
			$this->database_host	= $database_host;
			$this->database_port	= $database_port;
			
			//not sure why I don't pass $this->database_name directly
			if (!$this->connect($database_name, $database_host, $database_port)) return FALSE; 
			//else $this->obj_general	= new class_general();
			fwrite(STDOUT, "$this->class_name class constructor set.\n");
			return TRUE;
			
		} else return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 1, 1);
	} //<-- end function -->
	
	//************* changes data type of a given column of a given table *************
	function change_data_type($table, $column_name, $data_type) {
		if ($this->check_table_exists($table)) {
			if (!empty($column_name) && !empty($data_type)) {
				$sql = 'ALTER TABLE '.$table.' ALTER COLUMN '.$column_name.' TYPE '.$data_type;
				$res = @pg_query($sql);
				
				if ($this->sql_error = pg_last_error()) {
					class_general::get_errors($this->sql_error,__FUNCTION__,'SQL');
					return FALSE;
				} else {
					fwrite(STDOUT, 'Performed '.__FUNCTION__."on $this->num_rows records!\n");
					return TRUE;
				} //<-- end if -->
				
			} else return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 1, 1);
		} else return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 5, 1, $table);
	} //<-- end function -->
	
	//************* checks for table existance *************
	function check_table_exists($table) {
		if (empty($this->arr_tables)) class_pgsql::get_table_names(); // check to make sure $this->arr_tables is empty
		if (in_array($table, $this->arr_tables)) {
			fwrite(STDOUT, "Table $table exists!\n");
			return TRUE;
		} else return FALSE;
	} //<-- end function -->
	
	//************* clears existing table *************
	function clear_table($table) {
		if (class_pgsql::check_table_exists($table)) {		
			$sql = 'TRUNCATE TABLE '.$table;
			$res = @pg_query($sql);
				
			if ($this->sql_error = pg_last_error()) {
				class_general::get_errors($this->sql_error,__FUNCTION__,'SQL');
				return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 'SLQ Error, check php_errors.log', 1);
			} else {
				fwrite(STDOUT, "Table $table cleared!\n");
				return TRUE;
			} //<-- end if -->
			
		} else return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 5, 1, $table);
	} //<-- end function -->

	//************* COMMIT transaction *************
	function commit() {
		$sql = 'COMMIT';
		$res = @pg_query($sql) or trigger_error('SQL', E_USER_ERROR);
		fwrite(STDOUT, "----------------------\n");
		fwrite(STDOUT, "Transaction committed!\n");
		fwrite(STDOUT, "----------------------\n");
		return $res;
	} //<-- end function -->
	
	//************* establish a connection to the database *************
	function connect($database_name = NULL, $database_host = NULL, $database_port = NULL) {
		if(!$database_name) $database_name = $this->database_name; //not sure why I don't pass $this->database_name directly
		if(!$database_host) $database_host = $this->database_host;
		if(!$database_port) $database_port = $this->database_port;
		static $dbconn; // declared static to keep variable in scope after method ends
		
		if (!$dbconn) { //make sure there is no connection first
			$string = "dbname=$database_name host=$database_host port=$database_port";
			$dbconn = pg_connect($string);
			fwrite(STDOUT, "Connection complete!\n");
		} //<-- end if -->
		
		//if there is still no connection
		if (!$dbconn) return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 'Connection failed', 1);
		else return TRUE;
	} //<-- end function -->
	
	//************* creates a table *************
	// if table exists, use $mode 
	// 1 = overwrite, 2 = abort
	function create_table($table, $column_names, $data_types, $is_temp = FALSE, $is_null = FALSE, $mode = 2) {
		if (!empty($column_names) && !empty($data_types)) {
			if ($this->check_table_exists($table)) {
				switch ($mode) {
					case 1:
						drop_table($table);
						break;
					case 2:
						return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, "table $table already exists", 1);
					default:
						return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 4, 1);
				} //<-- end switch -->
			} //<-- end if -->
		
			$arr = array();
			if ($is_temp) $x = 'TEMP TABLE';
			else $x = 'TABLE';
			if ($is_null) $y = 'NULL';
			else $y = 'NOT NULL';
						
			$sql = "CREATE $x $table (";
			
			if (is_array($column_names) && is_array($data_types)) {
				$max = count($column_names);
				for ($i=0; $i<$max; $i++) $arr[] = "$column_names[$i] $data_types[$i] $y";
				$sql .= implode(',', $arr).')'; // convert array to string
				
			} elseif (!is_array($column_names) && (!is_array($data_types))) {
				$sql .="$column_names $data_types $y)";
				
			} else return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 'inconsistent data types', 1);
			
			$res = @pg_query($sql);
			
			if ($this->sql_error = pg_last_error()) {
				class_general::get_errors($this->sql_error,__FUNCTION__,'SQL');
				return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 'SLQ Error, check php_errors.log', 1);
			} else {
				fwrite(STDOUT, "Table $table created!\n");
				return TRUE;
			} //<-- end if -->
			
		} else return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 1, 1);
	} //<-- end function -->
	
	//************* drops existing table *************
	function drop_table($table) {
		if (!empty($table)) {		
			$sql = 'DROP TABLE IF EXISTS '.$table;
			$res = @pg_query($sql);
				
			if ($this->sql_error = pg_last_error()) {
				class_general::get_errors($this->sql_error,__FUNCTION__,'SQL');
				return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 'SLQ Error, check php_errors.log', 1);
			} else {
				fwrite(STDOUT, "Table $table dropped!\n");
				return TRUE;
			} //<-- end if -->
			
		} else return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 1, 1);
	} //<-- end function -->
	
	
	//************* finds columns of a given data types *************
	function find_columns($table, $arr_search_data_type) {
		if ($this->check_table_exists($table)) {
			if (!empty($arr_search_data_type)) {
				$arr_keys_to_replace	= array();
				$arr_effected_columns	= array();

				$this->get_data_types($this->arr_tables[$i]);
				$this->get_column_names($this->arr_tables[$i]);
	
				//get keys with search data type
				$arr_keys_to_replace = class_general::array_keys_intersect($this->arr_data_types, $arr_search_data_type);
				$max = count($arr_keys_to_replace);
								
				//<-- begin loop through each effected column -->
				for ($i=0; $i<$arr_effected_columns; $i++) {
					$arr_effected_columns[] = $this->arr_column_names[$arr_keys_to_replace[$i]];
				} //<-- end loop through each effected column -->
				
				fwrite(STDOUT, "Found $max columns\n");
				return $arr_effected_columns;
				
			} else return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 1, 2);
		} else return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 5, 2, $table);
	} //<-- end function -->
	
	//************* get column names from a given table *************
	function get_column_names($table) {	
		if ($this->check_table_exists($table)) {
			$sql = 'SELECT column_name FROM information_schema.columns '. 
				"WHERE table_name= '".$table.
				"'";
			
			unset($this->arr_column_names);
			$res = @pg_query($sql);
				
			if ($this->sql_error = pg_last_error()) {
				class_general::get_errors($this->sql_error,__FUNCTION__,'SQL');
				return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 'SLQ Error, check php_errors.log', 2);
			} //<-- end if -->
			
			$max_columns = pg_num_rows($res);
			
			//save query result
			for ($i=0; $i<$max_columns; $i++) {
				$arr[$i] = pg_fetch_row($res);
				$this->arr_column_names[] = $arr[$i][0]; 
			} //<-- end for -->
			
			fwrite(STDOUT, "Table $table column names retrieved!\n");
			return $this->arr_column_names;
			
		} else return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 5, 2, $table);
	} //<-- end function -->
		
	//************* get data types from a given table *************
	function get_data_types($table) {	
		if ($this->check_table_exists($table)) {
			$sql = "SELECT data_type FROM information_schema.columns ". 
				"WHERE table_name= '".$table.
				"'";
			
			unset($this->arr_data_types);
			$res = @pg_query($sql);
				
			if ($this->sql_error = pg_last_error()) {
				class_general::get_errors($this->sql_error,__FUNCTION__,'SQL');
				return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 'SLQ Error, check php_errors.log', 2);
			} //<-- end if -->
			
			$max_columns = pg_num_rows($res);
			
			//save query result
			for ($i=0; $i<$max_columns; $i++) {
				$arr[$i] = pg_fetch_row($res);
				$this->arr_data_types[] = $arr[$i][0]; 
			} //<-- end for -->
			
			fwrite(STDOUT, "Column $column_name data types retrieved!\n");
			return $this->arr_data_types;
			
		} else return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 5, 2, $table);
	} //<-- end function -->
	
	//************* get data values from a given column of a given table *************
	function get_data_values($table,$column_name) {
		if ($this->check_table_exists($table)) {
			if (!empty($column_name)) {
				$arr = array();
				$arr_data_values = array();
				$sql = "SELECT $column_name FROM $table";
				$res = @pg_query($sql);
				
				if ($this->sql_error = pg_last_error()) {
					class_general::get_errors($this->sql_error,__FUNCTION__,'SQL');
					return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 'SLQ Error, check php_errors.log', 2);
				} //<-- end if -->
				
				$max = pg_num_rows($res);
	
				//save query result
				for ($i=0; $i<$max; $i++) {
					$arr[$i] = pg_fetch_row($res);
					$arr_data_values[] = $arr[$i][0]; 
				} //<-- end for -->
				
				fwrite(STDOUT, "Column $column_name data values retrieved!\n");
				return $arr_data_values;
			
			} else return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 1, 2);
		} else return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 5, 2, $table);
	} //<-- end function -->

	//************* gets array of table names *************
	function get_table_names() {
		$arr = array();
		$sql = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';";
		$res = @pg_query($sql);
				
		if ($this->sql_error = pg_last_error()) {
			class_general::get_errors($this->sql_error,__FUNCTION__,'SQL');
			return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 'SLQ Error, check php_errors.log', 2);
		} //<-- end if -->

		$max = pg_num_rows($res);
		
		//save query result
		for ($i=0; $i<$max; $i++) {
			$arr[$i] = pg_fetch_row($res);
			$this->arr_tables[] = $arr[$i][0];
		} //<-- end for -->
		
		fwrite(STDOUT, "$max table names retrieved!\n");
		return $this->arr_tables;
	} //<-- end function -->
	
	//************* inserts records into a column of a given table *************
	function insert_records($table, $column_names, $data_values) {
		if ($this->check_table_exists($table)) {
			if (!empty($column_names) && !empty($data_values)) {
				$sql = 'INSERT INTO '.$table.' ('.$column_names.') VALUES '.$data_values.';';
				fwrite(STDOUT, "SQL: $sql\n");
				$res = @pg_query($sql);
				
				if ($this->sql_error = pg_last_error()) {
					class_general::get_errors($this->sql_error,__FUNCTION__,'SQL');
					return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 'SLQ Error, check php_errors.log', 1);
				} else {
					$this->num_rows = pg_affected_rows($res);
					fwrite(STDOUT, "Inserted $this->num_rows records!\n");
					return TRUE;
				} //<-- end if -->
				
			} else return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 1, 2);
		} else return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 5, 2, $table);
	} //<-- end function -->
	
	//************* changes case of values in a given array *************
	// $mode 
	// 1 = UPPERCASE, 2 = lowercase, 3 = Title Case
	function recase($arr_values, $mode = 1) {
		if (!empty($arr_values)) {
			$arr_recased_values= array();
			$max = count($arr_values);
			
			// switch to select the appropriate case function
			switch ($mode) {
				case 1:
					$case_func = strtoupper();
					break;
				case 2:
					$case_func = strtolower();
					break;
				case 3:
					$case_func = ucwords();
					break;
				default:
					return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 4, 2);
			} //<-- end switch -->
					
			//<-- begin loop through each value -->
			for ($i=0; $i<$max; $i++) {
				$column_name = $arr_column_names[$i];
				$arr_recased_values[] = $case_func($table, $arr_values[$i]);
			} //<-- end loop through each column -->

		fwrite(STDOUT, "$max values recased!\n");
		return $this->arr_recased_values;
		
		} else return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 1, 2);
	} //<-- end function -->
	
	//************* creates a regular select query *************
	function select_regular($table, $arr_columns, $column_w_keys = NULL, $where_column = NULL, $where_value = NULL) {
		if ($this->check_table_exists($table)) {
			if (!empty($arr_columns)) {
				if (!empty($where_column) && !empty($where_value)) $where = ' WHERE '.$where_column.' = '.$where_value;
				else $where = '';
				
				$arr_data_values 	= array();
				
				if (!empty($column_w_keys)) {
					$arr_column_names = array($column_w_keys);
					$select = $column_w_keys.', ';
				} else {
					$arr_column_names = array();
					$select = '';
				} //<-- end if -->
				
				$columns_w_values = implode(', ', $arr_columns); // convert array to string
				$sql = 'SELECT '.$select.$columns_w_values.' FROM '.$table.$where.';';
	
				//fwrite(STDOUT, "SQL: $sql\n");
				$res = @pg_query($sql);
				
				if ($this->sql_error = pg_last_error()) {
					class_general::get_errors($this->sql_error,__FUNCTION__,'SQL');
					return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 'SLQ Error, check php_errors.log', 1);
				} //<-- end if -->
				
				$max_values = pg_num_rows($res);

				//save query result
				for ($i=0; $i<$max_values; $i++) {
					$arr[$i] = pg_fetch_row($res);
					$arr_data_values[] = $arr[$i];
				} //<-- end for -->
				
				if (empty($arr_data_values)) {
					fwrite(STDOUT, "No regular values.\n");
					return NULL;					
				} //<-- end if -->
				
				//combine arrays
				$arr_column_names = array_merge($arr_column_names,$arr_columns);
				
				//load column names into the array keys
				for ($i=0; $i<$max_values; $i++) {
					$arr_data_values[$i] = array_combine($arr_column_names, $arr_data_values[$i]);
				} //<-- end for -->
				
				fwrite(STDOUT, "$max_values records selected!\n");
				return $arr_data_values;
				
			} else return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 1, 2);
		} else return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 5, 2, $table);
	} //<-- end function -->

	//************* creates a select query with a column lookup *************
	function select_matched($haystack_table, $needle_table, $needle_column, $needle_column2, $column_w_keys, $replacement_column) {
		if ($this->check_table_exists($needle_table) && $this->check_table_exists($haystack_table)) {
			if (!empty($column_w_keys) && !empty($needle_column) && !empty($replacement_column) && !empty($needle_column2)) {
				$arr_column_names 	= array($column_w_keys, $replacement_column);
				$arr_data_values 	= array();
				
				$sql = 'SELECT '.$needle_table.'.'.$column_w_keys.', '.$haystack_table.'.'.$replacement_column.
					' FROM '.$haystack_table.', '.$needle_table. 
					' WHERE '.$haystack_table.'.'.$needle_column2.' ILIKE '.$needle_table.'.'.$needle_column.';';
	
				//fwrite(STDOUT, "SQL: $sql\n");
				$res = @pg_query($sql);
				
				if ($this->sql_error = pg_last_error()) {
					class_general::get_errors($this->sql_error,__FUNCTION__,'SQL');
					return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 'SLQ Error, check php_errors.log', 1);
				} //<-- end if -->
				
				$max_values = pg_num_rows($res);
				
				//save query result
				for ($i=0; $i<$max_values; $i++) {
					$arr[$i] = pg_fetch_row($res);
					$arr_data_values[] = $arr[$i];
				} //<-- end for -->
	
				if (empty($arr_data_values)) {
					fwrite(STDOUT, "No matched values.\n");
					return NULL;					
				} //<-- end if -->
				
				//load column names
				for ($i=0; $i<$max_values; $i++) {
					$arr_data_values[$i] = array_combine($arr_column_names, $arr_data_values[$i]);
				} //<-- end for -->
				
				fwrite(STDOUT, "$max_values records selected!\n");
				return $arr_data_values;

			} else return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 1, 2);
		} else return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 5, 2, $table);
	} //<-- end function -->

	//************* creates a select query for unmatched lookup values *************
	function select_unmatched($haystack_table, $needle_table, $needle_column, $needle_column2, $copies) {
		if ($this->check_table_exists($haystack_table) && $this->check_table_exists($needle_table)) {
			if (!empty($needle_column) && !empty($needle_column2) && !empty($copies)) {
				$arr_data_values = array();
				
				$sql = 'SELECT '.$haystack_table.'.'.$needle_column. 
					' FROM '.$needle_table. 
					' RIGHT JOIN '.$haystack_table. 
					' ON '.$needle_table.'.'.$needle_column2.' ILIKE '.$haystack_table.'.'.$needle_column.
					' WHERE '.$needle_table.'.'.$needle_column2.' IS NULL'.
					' GROUP BY '.$haystack_table.'.'.$needle_column.
					' ORDER BY '.$haystack_table.'.'.$needle_column.';';
	 				
				// fwrite(STDOUT, "SQL: $sql\n");
				$res = @pg_query($sql);
				
				if ($this->sql_error = pg_last_error()) {
					class_general::get_errors($this->sql_error,__FUNCTION__,'SQL');
					return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 'SLQ Error, check php_errors.log', 1);
				} //<-- end if -->
				
				$max_values = pg_num_rows($res);
					
				// save query result
				// loop through each row
				for ($i=0; $i<$max_values; $i++) {
					$arr[$i] = pg_fetch_row($res);
					
					// loop through each copy (one liner)
					for ($j=0; $j<$copies; $j++) $arr_data_values[$i][] = $arr[$i][0];
					
				} //<-- end for loop -->
	
				if (empty($arr_data_values)) {
					fwrite(STDOUT, "No unmatched values.\n");
					return NULL;					
				} //<-- end if -->
				
				//$data_values = implode(", ", $arr_data_values); // convert array to string
				fwrite(STDOUT, "$max_values records selected!\n");
				return $arr_data_values;
				
			} else return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 1, 2);
		} else return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 'one of the tables does not exist', 1);
	} //<-- end function -->
	
	//************* start a new transaction terminated by either COMMIT or ROLLBACK *************
	function transaction() {
		$sql = 'BEGIN TRANSACTION';
		$res = @pg_query($sql) or trigger_error('SQL', E_USER_ERROR);
		fwrite(STDOUT, "------------------\n");
		fwrite(STDOUT, "Transaction begun!\n");
		fwrite(STDOUT, "------------------\n");
		return $res;
	} //<-- end function -->
	
	// ************* ROLLBACK transaction *************
	function rollback() {
		$sql = 'ROLLBACK';
		$res = @pg_query($sql) or trigger_error('SQL', E_USER_ERROR);
		fwrite(STDOUT, "--------------------\n");
		fwrite(STDOUT, "Transaction aborted!\n");
		fwrite(STDOUT, "--------------------\n");
		return $res;
	} //<-- end function -->

	//************* updates the record for a column of a given table *************
	function update_record_bycolumn($table, $column_name, $old_data_value, $new_data_value) {
		if ($this->check_table_exists($table)) {
			if (!empty($column_name) && !empty($old_data_value) && !empty($new_data_value)) {
				$sql = 'UPDATE '.$table.' SET '.$column_name.' = '."'".$new_data_value."'".
				' WHERE '.$column_name.' = '."'".$old_data_value."'".';';
				
				//fwrite(STDOUT, "SQL: $sql\n");
				$res = @pg_query($sql);
				
				if ($this->sql_error = pg_last_error()) {
					class_general::get_errors($this->sql_error,__FUNCTION__,'SQL');
					return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 'SLQ Error, check php_errors.log', 1);
				} else {
					$this->num_rows = pg_affected_rows($res);
					fwrite(STDOUT, 'Performed '.__FUNCTION__."on $this->num_rows records!\n");
					return TRUE;
				} //<-- end if -->
				
			} else return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 1, 2);
		} else return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 5, 2, $table);
	} //<-- end function -->
	
	//************* updates the records for all columns in needle table matching columns in haystack table *************
	function update_record_bytable($haystack_table, $needle_table, $arr_column_names, $join_column, $check_column) {
		if ($this->check_table_exists($haystack_table) && $this->check_table_exists($needle_table)) {
			foreach ($arr_column_names as $column) {
				$needle_columns .= $column.', ';
				$haystack_columns .= $haystack_table.'.'.$column.', ';
			} //<-- end foreach -->

			$needle_columns = rtrim($needle_columns, ', '); // remove trailing ','
			$haystack_columns = rtrim($haystack_columns, ', '); // remove trailing ','
								
			$sql = 'UPDATE '.$needle_table.' SET ('.$needle_columns.') = ('.$haystack_columns.')'.' FROM '.$haystack_table.
			' WHERE '.$needle_table.'.'.$join_column.' = '.$haystack_table.'.'.$join_column.
			' AND '.$needle_table.'.'.$check_column.' != '.$haystack_table.'.'.$check_column.';';
			
			//fwrite(STDOUT, "SQL: $sql\n");
			$res = @pg_query($sql);
			
			if ($this->sql_error = pg_last_error()) {
				class_general::get_errors($this->sql_error,__FUNCTION__,'SQL');
				return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 'SLQ Error, check php_errors.log', 1);
			} else {
				$this->num_rows = pg_affected_rows($res);
				fwrite(STDOUT, 'Performed '.__FUNCTION__."on $this->num_rows records!\n");
				return TRUE;
			} //<-- end if -->

		} else return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 'one of the tables does not exist', 1);
	} //<-- end function -->
} //<-- end class -->
?>
