<?php
//*****************************************************************************
// purpose: provides an interface to import a csv file into a Postgres database 
// notes:	much quicker (10-100 times) that line by line SQL INSERTs.
//*****************************************************************************

// include files
require_once 'class_general.inc';

//<-- begin class -->
class class_csv2postgres extends class_pgsql {
	var $arr_csv_columns 	= array();	// array of columns
	var $class_name 		= __CLASS__;// class name
	var $csv_columns;					// string of columns
	var $field_delimiter;		 		// character to separate fields
	var $field_escape_char;				// char to escape special symbols
	var $sql_error; 					// error message
	var $num_rows;						// number of rows
	var $use_csv_header; 				// use first line of file OR ("column1", "column2", etc.)

	//************* class constructor *************
	function class_csv2postgres($use_csv_header = TRUE, $field_delimiter = ",", $field_escape_char = "\"") {
		$this->use_csv_header 	= $use_csv_header;
		$this->field_delimiter 	= $field_delimiter;
		$this->field_escape_char= $field_escape_char;
		fwrite(STDOUT, "$this->class_name class constructor set.\n");
		return TRUE;
	}

	//************* creates an array of headers *************
	function create_header_fields($csv_file) {
		if (file_exists($csv_file)) {
			$arr = array();
			$fpointer = fopen($csv_file, 'r');			
			$arr = fgetcsv($fpointer, 10*1024, $this->field_delimiter);
			$max = count($arr) + 1;
			
			for($i=1; $i<$max; $i++) {
				if (trim($val)!="") $this->arr_csv_columns[] = 'column'.$i;
			} //<-- end for -->
			
			fclose($fpointer);
			fwrite(STDOUT, "CSV header files retrieved!\n");
			return $this->arr_csv_columns;
			
		} else return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 3, 2);
	} //<-- end function -->
	
	//************* returns array or list of CSV file headers *************
	// $mode: 1 = array, 2 = list					
	function get_csv_header_fields($csv_file, $mode = 2) {
		if (file_exists($csv_file)) {
			$fpointer = fopen($csv_file, 'r');		
			
			switch ($mode) {
				case 1:
					$this->arr_csv_columns = fgetcsv($fpointer, 10*1024, $this->field_delimiter);
					fclose($fpointer);
					fwrite(STDOUT, "CSV header array fields retrieved!\n");
					return $this->arr_csv_columns;
					break;
	
				case 2:			
					$this->csv_columns = rtrim(fgets($fpointer), "\n");
					fclose($fpointer);
					fwrite(STDOUT, "CSV header string fields retrieved!\n");
					return $this->csv_columns;
					break;
					
				default:
					return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 4, 2);
			} //<-- end switch -->
				
		} else return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 3, 2, $csv_file);
	} //<-- end function -->
						
	//************* imports csv file into table *************
	function import_csv($csv_file, $table, $header = NULL) {
		if (file_exists($csv_file)) {
			if (($this->check_table_exists($table))) {
				if ($this->use_csv_header) {
					$CSV = 'CSV HEADER';
					
					if (!$header) {
						$this->get_csv_header_fields($csv_file, 2);
						//$this->csv_columns = implode(",", $this->arr_csv_columns);
						$header = ' ('.$this->csv_columns.')';
					} else $header = ' ('.$header.')';
					
				} else {
					$CSV = 'CSV';
					$header = '';
				} //<-- end if -->
				
				$sql = 'COPY '.$table.$header." FROM '".@pg_escape_string($csv_file).
					"' WITH DELIMITER '".@pg_escape_string($this->field_delimiter)."' ".$CSV.
					" ESCAPE '".@pg_escape_string($this->field_escape_char)."' ";
			
				//fwrite(STDOUT, "$sql\n");	
				$res = @pg_query($sql);
				
				if ($this->sql_error = pg_last_error()) {
					class_general::get_errors($this->sql_error,__FUNCTION__,'SQL');
					return FALSE;
				} else {
					$this->num_rows = pg_affected_rows($res);
					fwrite(STDOUT, "Imported $this->num_rows rows into table $table!\n");
					return TRUE;
				} //<-- end if -->

			} else return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 5, 1, $table);
		} else return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 3, 1, $csv_file);
	} //<-- end function -->
} //<-- end class -->
?>