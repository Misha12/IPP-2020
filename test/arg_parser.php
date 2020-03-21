<?php
if (!isset($HELPER)) include './helper.php';

$ARG_PARSE = 1;

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

    // TODO Implement
    public function setHelp()
    {
    }

    // TODO Implement
    public function setDirectory($dir)
    {
    }

    // TODO Implement
    public function setRecursive()
    {
    }

    // TODO Implement
    public function setParseScript($filename)
    {
    }

    // TODO Implement
    public function setIntScript($filename)
    {
    }

    // TODO Implement
    public function setParseOnly()
    {
    }

    // TODO Implement
    public function setIntOnly()
    {
    }

    // TODO Implement
    public function setJexamxmlPath($path)
    {
        $this->jexamxml = $path;
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

        foreach (array_slice($argv, 1) as $arg) {
            switch ($arg) {
                case '--help':
                    $args->setHelp();
                    break;
                case '--recursive':
                    $args->setRecursive();
                    break;
                case '--parse-only':
                    $args->setParseOnly();
                    break;
                case '--int-only':
                    $args->setIntOnly();
                    break;
                default:
                    if (Helper::startsWith($arg, 'directory')) {
                        $args->setDirectory($this->getPathFromArgument($arg, 'directory'));
                        break;
                    } elseif (Helper::startsWith($arg, 'parse-script')) {
                        $args->setParseScript($this->getPathFromArgument($arg, 'parse-script'));
                        break;
                    } elseif (Helper::startsWith($arg, 'int-script')) {
                        $args->setIntScript($this->getPathFromArgument($arg, 'int-script'));
                        break;
                    } elseif (Helper::startsWith($arg, '--jexamxml')) {
                        $args->setJexamxmlPath($this->getPathFromArgument($arg, 'jexamxml'));
                        break;
                    } else {
                        echo $arg;
                        exit(1); // TODO: Error code and message.
                    }
            }
        }

        return $args;
    }

    private function getPathFromArgument($str, $key)
    {
        return preg_match("/--$key=(.+)/", $str, $matches) ? $matches[1] : null;
    }
}
