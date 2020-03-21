<?php
include './arg_parser.php';

class Program
{
    private $commandLineParser;

    public function __construct()
    {
        $this->commandLineParser = new CommandLineArgsParseService();
    }

    public function Run($argc, $argv)
    {
        $args = $this->commandLineParser->parse($argc, $argv);

        var_dump($args);
        echo "RunAll: ".$args->runAll();
    }
}

$program = new Program();
$program->Run($argc, $argv);
