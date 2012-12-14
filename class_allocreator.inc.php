<?php
//*****************************************************************************
// purpose: contains specfic allocreator functions 
//*****************************************************************************

// Configuration
$projects_dir	= dirname(dirname(dirname(__FILE__)));

//include files
require_once $projects_dir.'/library/class_general.inc';
require_once 'class_pgsql.inc';
require_once 'class_csv2postgres.inc';
require_once 'class_yahoo_quote.inc';

//<-- begin class -->
class class_allocreator {
	var $class_name 	= __CLASS__;	// class name
	var $database_name;					// database name
	var $database_host;					// database host
	var $database_port;					// database port
	var $project_loc;					// project directory
	var $select_dir;					// directory for saving output files
	var $join_dir;						// directory for saving files to join
	var $joined_dir;					// directory for saving joined files
	var $converted_dir;					// directory for saving files that have been converted to csv
	var $csv_dir;						// directory for saving csv files 
	var $imported_dir;					// directory for saving files that have been imported into db
	var $def_ext;						// def extention for output files
	var $csv_ext;						// def extention for csv files
	
	//************* class constructor *************
	function class_allocreator($database_name, $database_host, $database_port, $project_loc, $select_dir, $join_dir, $joined_dir, $converted_dir, $csv_dir, $imported_dir, $def_ext, $csv_ext) {
		if (!empty($database_name)) {
			$this->database_name	= $database_name;
			$this->database_host	= $database_host;
			$this->database_port	= $database_port;
			$this->project_loc		= $project_loc;
			$this->select_dir		= $select_dir;
			$this->join_dir			= $join_dir;
			$this->joined_dir		= $joined_dir;
			$this->converted_dir	= $converted_dir;
			$this->csv_dir			= $csv_dir;
			$this->imported_dir		= $imported_dir;
			$this->def_ext			= $def_ext;
			$this->csv_ext			= $csv_ext;
			
			if (!class_pgsql::connect($this->database_name, $this->database_host, $this->database_port)) return FALSE;
			fwrite(STDOUT, "$this->class_name class constructor set.\n");
			return TRUE;
			
		} else return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 1, 1);
	} //<-- end function -->
	
	//************* creates csvfiles in csv_dir *************
	function create_csvfiles($arr_files = NULL) {
		if (!$arr_files) {
			$arr_filenames = class_general::get_arr_filenames($this->select_dir, $this->def_ext);
			$arr_files = class_general::filename2file($arr_filenames, $this->select_dir);
		} else $arr_filenames = class_general::file2filename($arr_files);
		
		if (!$arr_filenames) return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 6, 2);
		$max_files = count($arr_filenames);
		$arr_table_names = class_general::extract_part($arr_filenames,"[");
		if (!$arr_table_names) return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 6, 2);
		$arr_arrays = class_general::unserialize_batch($arr_files);
		$arr_csvfiles = array();
		
		for ($i=0; $i<$max_files; $i++) {
			$filenum = class_general::countfiles($this->csv_dir, $this->csv_ext) + 1;
			$csvfile = $this->csv_dir.'/'.$arr_table_names[$i].'['.$filenum.'].'.$this->csv_ext;
			
			if (class_general::array2csv($arr_arrays[$i], $csvfile)) { // check to make sure array is converted to csv
				$check = class_general::move_file($arr_files[$i], $converted_dir); // check to make sure file is moved
				if (!check) $errors = TRUE;
				else $arr_csvfiles[] = $csvfile; 
			} else $errors = TRUE;
		} //<-- end for -->
		
		if ($errors) return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 6, 2);
		$max_files = count($arr_csvfiles);
		
		fwrite(STDOUT, "Created $max_files csvfiles!\n");
		return $arr_csvfiles;
	} //<-- end function -->

	//************* creates joinfiles in join_dir *************
	function create_joinfile($arr_results) {
		if (!empty($arr_results)) {
			$serial_results = serialize($arr_results); // save data in format that can be written to file
			$size = strlen($serial_results);
			$filenum = class_general::countfiles($this->join_dir) + 1;
			$joinfile = $this->join_dir.'/'.$size.'.'.$filenum;
			$check = class_general::write2file($serial_results, $joinfile); // write data to file
			if (!$check) return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 6, 2);

			fwrite(STDOUT, "Created joinfile $joinfile!\n");
			return $joinfile;
		} else return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 1, 2);
	} //<-- end function -->
	
	//************* creates outfile in select_dir *************
	function create_outfile($dest_table, $arr_results, $arr_keys = NULL) {
		if (class_pgsql::check_table_exists($dest_table)) {
			if (!empty($arr_results)) {
				if (!is_array(current($arr_results))) $arr_results = array($arr_results); // patch for array2string if there is only one row
				$arr_results = class_general::array2string($arr_results, $arr_keys); // convert array to a more simplified form
				if (empty($arr_results)) return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 1, 2);
				$serial_results = serialize($arr_results); // save data in format that can be written to file
				$filenum = class_general::countfiles($this->select_dir, $this->def_ext) + 1;
				$outfile = $this->select_dir.'/'.$dest_table.'['.$filenum.'].'.$this->def_ext;
				$check = class_general::write2file($serial_results, $outfile); // write data to file
				if (!$check) return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 6, 2);
	
				fwrite(STDOUT, "Created outfile $outfile!\n");
				return array($outfile);
			} else return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 1, 2);
		} else return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 5, 2, $dest_table);
	} //<-- end function -->

	//************* inserts csvfiles into database *************
	function import_csvfiles($arr_files = NULL, $cleartable = NULL) {
		if (!$arr_files) {
			$arr_filenames = class_general::get_arr_filenames($this->csv_dir, $this->csv_ext);
			$arr_files = class_general::filename2file($arr_filenames, $this->csv_dir);
		} else $arr_filenames = class_general::file2filename($arr_files);
		
		if (!$arr_filenames) fwrite(STDOUT, "No csvfiles to import\n");
		$max_files = count($arr_filenames);
		$arr_table_names = class_general::get_arr_base($arr_filenames);
		$arr_table_names = class_general::extract_part($arr_table_names,"[");
		if (!$arr_table_names) return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 6, 1);
		
		for ($i=0; $i<$max_files; $i++) { // import csv into postgres
			class_pgsql::transaction(); // begin transaction
			if ($cleartable) class_pgsql::clear_table($arr_table_names[$i]);
			if (class_csv2postgres::import_csv($arr_files[$i], $arr_table_names[$i], $header)) {
				class_pgsql::commit(); // commit transaction
				class_general::move_file($arr_files[$i], $imported_dir);
			} else {
				class_pgsql::rollback(); // rollback transaction
				$errors = TRUE;
			} //<-- end if -->
		} //<-- end for -->
		
		if ($errors) return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 6, 1);
		
		fwrite(STDOUT, "Imported $max_files csvfiles!\n");
		return TRUE;
	} //<-- end function -->
	
	//************* joins files in join_dir *************
	function joinfiles($dest_table, $arr_files = NULL, $arr_append = NULL) {
		if (class_pgsql::check_table_exists($dest_table)) {
			if (!$arr_files) $arr_filenames = class_general::get_arr_filenames($this->join_dir);
			else $arr_filenames = class_general::file2filename($arr_files);
			if (!$arr_filenames) return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 6, 2);
			rsort($arr_filenames, SORT_NUMERIC);
			$arr_files = class_general::filename2file($arr_filenames, $this->join_dir);
			$arr_arrays = class_general::unserialize_batch($arr_files);
			$arr_joined = class_general::array_compress($arr_arrays);
			if (!$arr_joined) return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 6, 2);
			
			if ($arr_append) {
				$arr_joined = class_general::array_append($arr_joined, $arr_append);
				if (!$arr_joined) return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 6, 2);
			} //<-- end if -->

			$serial_joined = serialize($arr_joined); // save data in format that can be written to file
			$filenum = $general->countfiles($this->select_dir, $this->def_ext) + 1;
			$outfile = $this->select_dir.'/'.$dest_table.'['.$filenum.'].'.$this->def_ext;
			$check = class_general::write2file($serial_joined, $outfile); // write joined data to file
			if (!$check) return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 6, 2);
			$i = 0;
			
			foreach ($arr_files as $file) { //
				$check = class_general::move_file($file, $joined_dir);
				if (!$check) $errors = TRUE;
			} //<-- end foreach -->
			
			if ($errors) return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 6, 2);
			
			fwrite(STDOUT, "Joined $i joinfiles!\n");
			return $outfile;
		} else return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 5, 1, $dest_table);
	} //<-- end function -->	
} //<-- end class -->