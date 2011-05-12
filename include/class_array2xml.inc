<?php
//*********************************************************************
// Convert an array or multi-dimentional array to XML
// http://phpro.org/classes/PHP-Recursive-Array-To-XML-With-DOM.html
//*********************************************************************

// include files
include('XML/Serializer.php');

//<-- begin class -->
class class_array2xml extends DomDocument {
	var $xpath;
	var $root;			// The name of the root node
	var $numeric_node; 	// The name numeric keys are called
	var $verbose;		// verbose output
	
	//************* class constructor *************
	function __construct($verbose = FALSE, $root = 'root', $numeric_node = 'numeric') {
		parent::__construct();		
		$this->verbose		= $verbose;
		$this->encoding 	= 'ISO-8859-1'; 		// set the encoding
		$this->formatOutput = true; 				// format the output
		$this->numeric_node = $numeric_node; 		// set the node names
		$this->root 		= $this->appendChild($this->createElement($root)); // create the root element
		$this->xpath 		= new DomXPath($this);
	}

	//************* creates a DOM XML *************
	function createNode($arr_data) {		
		foreach($arr_data as $element => $value) {
			$element = is_numeric($element) ? $this->numeric_node : $element;
			$child = $this->createElement($element, (is_array($value) ? null : $value));
			$this->root->appendChild($child);
			if(is_array($value)) self::createNode($value, $child);
		}
	} //<-- end function -->
	
	//************* creates XML with XMLSerializer *************
	function XMLserialize($arr_data) {
		$serializer_options = array (
			'addDecl' => TRUE,				
			'encoding' => $this->encoding,
			'indent' => '	',
			'rootName' => $this->root, 	
			'defaultTagName' => $this->numeric_node
		);

		$serializer = new XML_Serializer($serializer_options);	            
		$res = $serializer->serialize($arr_data); 		// perform serialization
		
		if(!PEAR::isError($res)) {
			if($this->verbose) fwrite(STDOUT, "array created!\n");
			$xml = $serializer->getSerializedData();	
			return $xml;
		} else {
			$message = $res->getMessage();
			return class_general::return_error(__CLASS__, __FUNCTION__, __LINE__, 0, 1, $message);
		} //<-- end if -->
	} //<-- end function -->
		
	//************* returns the generated XML as a string *************
	function __toString() {
		return $this->saveXML();
	} //<-- end function -->
	
	//************* perform an XPath query on the generated XML *************
	function query($query) {
		return $this->xpath->evaluate($query);
	} //<-- end function -->
} //<-- end class -->
?>