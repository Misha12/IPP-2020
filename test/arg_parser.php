<?php
if (!isset($HELPER)) include 'helper.php';
if (!isset($APP_CODES)) include 'app_codes.php';

$ARG_PARSE = 1;

/**
 * Trida pro uchovavani nactenych parametru prikazove radky.
 */
class CommandLineArguments
{
    public $help = false;
    public $directory = '.';
    public $recursive = false;
    public $parseScript = 'parse.php';
    public $intScript = 'interpret.py';
    public $parseOnly = false;
    public $intOnly = false;
    public $jexamxml = '/pub/courses/ipp/jexamxml/jexamxml.jar';

    public function setDirectory($dir)
    {
        $this->checkExists($dir, true);
        $this->directory = $dir;
    }

    public function setParseScript($filepath)
    {
        $this->checkExists($filepath);
        $this->parseScript = $filepath;
    }

    public function setIntScript($filepath)
    {
        $filepath = realpath($filepath);
        $this->checkExists($filepath);
        $this->intScript = $filepath;
    }

    public function setJexamxmlPath($path)
    {
        $path = realpath($path);
        $this->checkExists($path);
        $this->jexamxml = $path;
    }

    private function checkExists($path, $isDirectory = false)
    {
        if (!file_exists($path)) {
            $type = $isDirectory ? 'Directory' : 'File';
            throw new ErrorException("$type '$path' not exists", AppCodes::CannotOpenInputFileOrDirectory);
        }
    }
}

/**
 * Sluzba pro nacitani parametru prikazove radky.
 */
class CommandLineArgsParseService
{
    /**
     * Hlavni funkce pro nacitani parametru prikazove radky.
     *
     * @param int $argc Pocet parametru zadanych na prikazove radce (obsahuje i cestu a nazev skriptu v polozce na prvnim indexu).
     * @param int $argv Parametry zadane na prikazove radce.
     * @return CommandLineArguments
     */
    public function parse($argc, $argv)
    {
        if ($argc == 1)
            return new CommandLineArguments();

        try {
            return $this->parseArguments($argv);
        } catch (ErrorException $e) {
            Helper::errorExit($e->getCode(), $e->getMessage());
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
        $optArgs = getopt("", ["help", "directory:", "recursive", "parse-script:", "int-script:", "parse-only", "int-only", "jexamxml:"]);

        if (key_exists("help", $optArgs)) {
            if (count($args) > 1)
                throw new ErrorException("--help cannot be combined with another parameters.", AppCodes::InvalidParameters);

            $args->help = true;
        }

        $args->recursive = key_exists("recursive", $optArgs);
        $args->intOnly = key_exists("int-only", $optArgs);
        $args->parseOnly = key_exists("parse-only", $optArgs);

        if (key_exists("directory", $optArgs)) $args->setDirectory($args["directory"]);
        if (key_exists("parse-script", $optArgs)) $args->setParseScript($args["parse-script"]);
        if (key_exists("int-script", $optArgs)) $args->setIntScript($optArgs["int-script"]);
        if (key_exists("jexamxml", $optArgs)) $args->setJexamxmlPath($optArgs["jexamxml"]);

        if ($args->parseOnly && $args->intOnly)
            throw new ErrorException("--int-only and --parse-only cannot be combined.", AppCodes::InvalidParameters);

        if ($args->parseOnly && key_exists("int-script", $optArgs))
            throw new ErrorException("--int-script cannot be combined with --parse-only", AppCodes::InvalidParameters);

        if ($args->intOnly && key_exists("parse-script", $optArgs))
            throw new ErrorException("--parse-script cannot be combined with --int-only", AppCodes::InvalidParameters);

        return $args;
    }
}
