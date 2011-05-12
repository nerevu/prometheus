#!/usr/bin/php
<?php
	include "error2.php";
	//include "error.php";
	$file = 'foobar.log';
	fwrite(STDOUT,"Opening file $file\n");
	
	if (file_exists($file)) {
	   $fp = fopen($file,'r');
	   fclose($fp);
	   fwrite(STDOUT,"Job finished.\n");
	   exit(0);
	} else {
		trigger_error("File doesn't exist", E_USER_ERROR);
		fwrite(STDERR,"Warning: File $file doesn't exist.\n");
		exit(1);
	}
?>