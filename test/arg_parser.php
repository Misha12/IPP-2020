<?php
if (!isset($HELPER)) include './helper.php';
if (!isset($APP_CODES)) include './app_codes.php';

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

    // TODO Pokud je help == true, tak zakazat dalsi kombinace. Pokud bude, tak chyba 10.
    // TODO Pokud už byl jednou parametr nastaven, tak další volání ignorovat.

    public function setHelp()
    {
        $this->help = true;
    }

    public function setDirectory($dir)
    {
        $this->checkExists($dir, true);
        $this->directory = $dir;
    }

    public function setRecursive()
    {
        $this->recursive = true;
    }

    public function setParseScript($filepath)
    {
        // TODO Muze se zde objevit i cesta?
        // TODO Mame zohlednit parametr --directory?
        $this->checkExists($filepath);
        $this->parseScript = $filepath;
    }

    public function setIntScript($filepath)
    {
        // TODO Muze se zde objevit i cesta?
        // TODO Mame zohlednit parametr --directory?
        $this->checkExists($filepath);
        $this->intScript = $filepath;
    }

    public function setParseOnly()
    {
        // TODO Nepovolit kombinaci s --int-only, --int-script
        $this->parseOnly = true;
    }

    public function setIntOnly()
    {
        // TODO Nepovolit kombinaci s --parse-only, --parse-script

        $this->intOnly = true;
    }

    public function setJexamxmlPath($path)
    {
        $this->checkExists($path);
        $this->jexamxml = $path;
    }

    private function checkExists($path, $isDirectory = false)
    {
        if (!file_exists($path)) {
            $type = $isDirectory ? 'Directory' : 'File';
            throw new ErrorException("$type '$path' not exists", AppCodes::CannotOpenFileOrDirectory);
        }
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
                    if (Helper::startsWith($arg, '--directory')) {
                        $args->setDirectory($this->getPathFromArgument($arg, 'directory'));
                        break;
                    } elseif (Helper::startsWith($arg, '--parse-script')) {
                        $args->setParseScript($this->getPathFromArgument($arg, 'parse-script'));
                        break;
                    } elseif (Helper::startsWith($arg, '--int-script')) {
                        $args->setIntScript($this->getPathFromArgument($arg, 'int-script'));
                        break;
                    } elseif (Helper::startsWith($arg, '--jexamxml')) {
                        $args->setJexamxmlPath($this->getPathFromArgument($arg, 'jexamxml'));
                        break;
                    } else {
                        break;
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
