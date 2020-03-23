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
        $this->checkExists($filepath);
        $this->parseScript = $filepath;
    }

    public function setIntScript($filepath)
    {
        $this->checkExists($filepath);
    }

    public function setParseOnly()
    {
        $this->parseOnly = true;
    }

    public function setIntOnly()
    {
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
        print_r($argv);
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

        if (in_array('--help', $argv) && count($argv) > 2) {
            $joined = implode(' ', array_slice($argv, 1));
            throw new ErrorException("Unallowed combination of parameter. ($joined)", AppCodes::UnallowedParameterCombination);
        }

        if (in_array("--parse-only", $argv)) {
            foreach ($argv as $arg) {
                if ($arg == '--int-only' || Helper::startsWith($arg, '--int-script')) {
                    throw new ErrorException("--int-only or --int-script are disabled in combination with --parse-only.", AppCodes::UnallowedParameterCombination);
                }
            }
        } elseif (in_array('--int-only', $argv)) {
            foreach ($argv as $arg) {
                if ($arg == '--parse-only' || Helper::startsWith($arg, '--parse-script')) {
                    throw new ErrorException("--parse-only or --parse-script are disabled in combination with --int-only.", AppCodes::UnallowedParameterCombination);
                }
            }
        }

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
