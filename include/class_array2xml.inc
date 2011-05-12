<?php
//*********************************************************************
// Convert an array or multi-dimentional array to XML
// http://phpro.org/classes/PHP-Recursive-Array-To-XML-With-DOM.html
// @author Kevin Waterson
// @copyright 2009 PHPRO.ORG
//*********************************************************************
 
//<-- begin class -->
class array2xml extends DomDocument {
	public $nodeName;
	private $xpath;
	private $root;		// The name of the root node
	private $node_name; // The name numeric keys are called
	
	//************* class constructor *************
	public function __construct($root = 'root', $node_name = 'node') {
		parent::__construct();		
		$this->encoding = "ISO-8859-1"; // set the encoding
		$this->formatOutput = true; 	// format the output
		$this->node_name = $node_name; 	// set the node names
		$this->root = $this->appendChild($this->createElement($root)); // create the root element
		$this->xpath = new DomXPath($this);
	}

	//************* creates the XML representation of the array *************
	public function createNode($arr_data, $node = null) {
		if (is_null($node)) $node = $this->root;
		
		foreach($arr_data as $element => $value) {
			$element = is_numeric($element) ? $this->node_name : $element;
			$child = $this->createElement($element, (is_array($value) ? null : $value));
			$node->appendChild($child);
			if (is_array($value)) self::createNode($value, $child);
		}
	}

	//************* returns the generated XML as a string *************
	public function __toString() return $this->saveXML();

	//************* perform an XPath query on the generated XML *************
	public function query($query) return $this->xpath->evaluate($query);
} //<-- end class -->
?>