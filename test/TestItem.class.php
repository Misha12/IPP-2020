<?php
if (!isset($APP_CONSTS)) include 'Consts.class.php';

$TEST_ITEM = 1;

class TestResult
{
    public $parseResult = null;
    public $intResult = null;
}

class TestPartResult
{
    public $expectedExitCode = 0;
    public $realExitCode = 0;
    public $stdoutFile = null;
    public $stderrFile = null;
    public $stdoutContent = null;
    public $stderrContent = null;
    public $xmlState = 'not_tested';

    public function clean()
    {
        if (file_exists($this->stdoutFile))
            @unlink($this->stdoutFile);

        if (file_exists($this->stderrFile))
            @unlink($this->stderrFile);
    }

    public function isOk()
    {
        return $this->expectedExitCode === $this->realExitCode;
    }
}

/**
 * Trida reprezentujici jeden test.
 */
class TestItem
{
    public $path;
    public $name;

    public $srcExists = false;
    public $inputExists = false;
    public $outputExists = false;
    public $returnCodeExists = false;

    public function __construct($name, $path)
    {
        $this->path = $path;
        $this->name = $name;
    }

    private function getFullPath()
    {
        return $this->path . DIRECTORY_SEPARATOR . $this->name;
    }

    public function initTest($config)
    {
        if (!$this->srcExists)
            throw new Exception("Source file '" . $this->name . "' not found.");

        if (!$this->inputExists)
            touch($this->getFullPath() . ".in");

        if (!$this->outputExists)
            touch($this->getFullPath() . ".out");

        if (!$this->returnCodeExists)
            file_put_contents($this->getFullPath() . ".rc", "0");
    }

    public function runTest($config)
    {
        $result = new TestResult();

        if (!$config->intOnly)
            $result->parseResult = $this->runParserTest($config);

        if (!$config->parseOnly)
            $result->intResult = $this->runInterpretTest($config, $result->parseResult);

        // TODO: IPPCode20 -> XML -> Interpret.
        // TODO: Úklid dočasných souborů po testech.

        $result->parseResult->clean();
        return $result;
    }

    private function runInterpretTest($config, $parseTestResult)
    {
        output("Starting interpret test " . $this->name, true);
        return true;
    }

    /**
     * Spusteni testu analyzatoru kodu.
     *
     * @param CommandLineArguments $config
     * @return TestPartResult
     */
    private function runParserTest($config)
    {
        $result = new TestPartResult();
        $fullPath = $this->getFullPath();

        $result->expectedExitCode = intval(trim(file_get_contents($this->getFullPath() . ".rc")));
        $result->stdoutFile = "$fullPath.out_tmp";
        $result->stderrFile = "$fullPath.err_tmp";

        $phpExecutablePath = PHP_EXECUTABLE . " \"" . $config->parseScript . "\" < \"$fullPath.src\" > \"" . $result->stdoutFile . "\" 2> \"" . $result->stderrFile . "\"";
        exec($phpExecutablePath, $output, $retCode);

        $result->realExitCode = $retCode;
        $result->stdoutContent = file_get_contents($result->stdoutFile);
        $result->stderrContent = file_get_contents($result->stderrFile);

        if ($retCode < 30 && $result->expectedExitCode != $retCode) return $result;
        if (!$config->parseOnly || $retCode != 0) return $result;

        $jexamxmlExecutablePath = JAVA_EXECUTABLE . " " . $config->jexamxml . " \"$fullPath.out\" \"" . $result->stdoutFile . "\" xml_diff.xml /D \"" . dirname($config->jexamxml) . "/options\"";
        exec($jexamxmlExecutablePath, $output, $retCode);
        @unlink("xml_diff.xml");

        if ($retCode != 0) {
            $result->xmlState = "different_xml";
            return $result;
        }

        $result->xmlState = "ok";
        return $result;
    }
}
