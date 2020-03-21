<?php
class CommandLineArguments
{
    public $help = false;
    public $directory = '';
    public $recursive = false;
    public $parseScript = 'parse.php';
    public $intScript = 'interpret.py';
    public $parseOnly = false;
    public $intOnly = false;
    public $jexamxml = '/pub/courses/ipp/jexamxml/jexamxml.jar';

    public function __construct()
    {
        $this->directory = getcwd();
    }

    public function runAll()
    {
        return !$this->parseOnly && !$this->intOnly && !$this->help;
    }

    public function setHelp() {

    }

    public function setDirectory($dir) {

    }

    public function setRecursive() {

    }

    public function setParseScript($filename) {

    }

    public function setIntScript($filename) {

    }

    public function setParseOnly() {

    }

    public function setIntOnly() {

    }

    public function setJexamxmlPath($path) {

    }
}

class CommandLineArgsParseService
{
    public function parse($argc, $argv)
    {
        if ($argc == 1)
            return new CommandLineArguments();

        try {
            return $this->parseArguments($argv);
        } catch (ErrorException $e) {
            // TODO Zabíjení aplikace, když nastane chyba.
        }
    }

    /**
     * Nacitani parametru prikazove radky.
     *
     * @param mixed $argv
     * @return CommandLineArguments
     */
    private function parseArguments($argv)
    {
        $args = new CommandLineArguments();

        // TODO: Kombinování parametrů
        // TODO: Duplicitní parametry.

        foreach ($argv as $arg) {
            $this->trySetValue($arg, 'help', $args->help);
            $this->trySetValue($arg, 'recursive', $args->recursive);
            $this->trySetValue($arg, 'parse-only', $args->parseOnly);
            $this->trySetValue($arg, 'int-only', $args->intOnly);
            $this->trySetPath($arg, 'directory', $args->directory);
            $this->trySetPath($arg, 'parse-script', $args->parseScript);
            $this->trySetPath($arg, 'int-script', $args->intScript);
            $this->trySetPath($arg, 'jexamxml', $args->jexamxml);
        }

        return $args;
    }

    private function trySetValue($currentVal, $key, &$output)
    {
        if ($currentVal == "--$key") {
            $output = true;
        }
    }

    private function trySetPath($currentVal, $key, &$path)
    {
        if (preg_match("/--$key=(.+)/", $currentVal, $matches)) {
            $path = $matches[1];
        }
    }
}
