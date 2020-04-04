<?php
if (!isset($APP_CONSTS)) include 'Consts.class.php';

$TEST_ITEM = 1;

class TestResult
{
    /**
     * Vysledky testu analyzatoru kodu.
     * @var TestPartResult
     */
    public $parseResult = null;

    /**
     * Vysledky testu interpretu.
     * @var TestPartResult
     */
    public $intResult = null;

    public function isOk()
    {
        if ($this->parseResult != null) {
            if ($this->parseResult->expectedExitCode < 30 && $this->parseResult->expectedExitCode != $this->parseResult->realExitCode)
                return false;

            if ($this->parseResult->diffState != 'not_tested' && $this->parseResult->diffState != 'ok')
                return false;
        }

        if ($this->intResult != null) {
            if ($this->intResult->expectedExitCode != $this->intResult->realExitCode)
                return false;

            if ($this->intResult->diffState != 'not_tested' && $this->intResult->diffState != 'ok')
                return false;
        }

        return true;
    }

    public function getMessage()
    {
        if ($this->parseResult != null)
            return $this->parseResult->getMessage();

        if ($this->intResult != null)
            return $this->intResult->getMessage();

        return null;
    }
}

class TestPartResult
{
    public $expectedExitCode = 0;
    public $realExitCode = 0;
    public $stdoutFile = null;
    public $stderrFile = null;
    public $diffState = 'not_tested';

    private $stdout = null;
    private $stderr = null;
    public $diffResult = null;

    public function clean()
    {
        $isOk = $this->isOk();

        if (file_exists($this->stdoutFile)) {
            if (!$isOk)
                $this->stdout = file_get_contents($this->stdoutFile);

            @unlink($this->stdoutFile);
        }

        if (file_exists($this->stderrFile)) {
            if (!$isOk)
                $this->stderr = file_get_contents($this->stderrFile);

            @unlink($this->stderrFile);
        }
    }

    public function isOk()
    {
        if ($this->expectedExitCode !== $this->realExitCode)
            return false;

        if ($this->diffState != 'not_tested' && $this->diffState != 'ok')
            return false;

        return true;
    }

    public function getMessage()
    {
        if ($this->expectedExitCode !== $this->realExitCode) {
            return ('Neočekávaný návratový kód: ' . $this->realExitCode . '. Očekáváno: ' . $this->expectedExitCode) . '<br>' .
                (empty($this->stdout) ? null : '<b>STDOUT:</b> &nbsp;&nbsp;&nbsp;' . htmlspecialchars($this->stdout) . '<br>') .
                (empty($this->stderr) ? null : '<b>STDERR:</b> &nbsp;&nbsp;&nbsp;' . htmlspecialchars($this->stderr));
        }

        if ($this->diffState === 'different')
            return 'Rozdílný výstup<br><pre>' . $this->diffResult . "</pre>";

        return null;
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
        return realpath($this->path) . DIRECTORY_SEPARATOR . $this->name;
    }

    public function initTest($config)
    {
        if (!$this->srcExists)
            throw new Exception("Source file '" . $this->name . "' not found.");

        if (!$this->inputExists) touch($this->getFullPath() . ".in");
        if (!$this->outputExists) touch($this->getFullPath() . ".out");
        if (!$this->returnCodeExists) file_put_contents($this->getFullPath() . ".rc", "0");
    }

    public function runTest($config)
    {
        $result = new TestResult();

        if (!$config->intOnly)
            $result->parseResult = $this->runParserTest($config);

        if (!$config->parseOnly)
            $result->intResult = $this->runInterpretTest($config, $result->parseResult);

        if ($result->parseResult != null) $result->parseResult->clean();
        if ($result->intResult != null) $result->intResult->clean();

        return $result;
    }

    /**
     * Spusteni testu interpretace.
     *
     * @param CommandLineArguments $config
     * @param TestPartResult $parseTestResult
     * @return TestPartResult
     */
    private function runInterpretTest($config, $parseTestResult)
    {
        $result = new TestPartResult();
        $fullPath = $this->getFullPath();

        $result->expectedExitCode = intval(trim(file_get_contents("$fullPath.rc")));
        $result->stdoutFile = "$fullPath.int_out_tmp";
        $result->stderrFile = "$fullPath.int_err_tmp";

        $sourceCode = $parseTestResult != null ? $parseTestResult->stdoutFile : "$fullPath.src";
        $dataRedirection = "< \"$fullPath.in\" > \"" . $result->stdoutFile . "\" 2> \"" . $result->stderrFile . "\"";
        $pythonExecutablePath = PYTHON_EXECUTABLE . " \"" . $config->intScript . "\" --source=\"$sourceCode\" $dataRedirection";
        exec($pythonExecutablePath, $output, $retCode);

        $result->realExitCode = $retCode;
        if ($result->expectedExitCode != $retCode) return $result;
        if ($retCode != 0) return $result;

        exec(DIFF_EXECUTABLE . " \"$fullPath.out\" \"" . $result->stdoutFile . "\"", $output, $retCode);
        if ($retCode != 0) {
            $result->diffState = 'different';

            $filteredDiff = array_filter($output, function ($line) {
                return strlen($line) > 0 && $line[0] != '\\';
            });
            $result->diffResult = implode(PHP_EOL, $filteredDiff);

            return $result;
        }

        $result->diffState = 'ok';
        return $result;
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

        $result->expectedExitCode = intval(trim(file_get_contents($fullPath . ".rc")));
        $result->stdoutFile = "$fullPath.out_tmp";
        $result->stderrFile = "$fullPath.err_tmp";

        $phpExecutablePath = PHP_EXECUTABLE . " \"" . $config->parseScript . "\" < \"$fullPath.src\" > \"" . $result->stdoutFile . "\" 2> \"" . $result->stderrFile . "\"";
        exec($phpExecutablePath, $output, $retCode);

        $result->realExitCode = $retCode;
        if ($result->expectedExitCode < 30 && $result->expectedExitCode != $retCode) return $result;
        if (!$config->parseOnly || $retCode != 0) return $result;

        $jexamxmlExecutablePath = JAVA_EXECUTABLE . " " . $config->jexamxml . " \"$fullPath.out\" \"" . $result->stdoutFile . "\" xml_diff.xml /D \"" . $config->jexamxmlConfig . "\"";
        exec($jexamxmlExecutablePath, $output, $retCode);
        @unlink("xml_diff.xml");

        if ($retCode != 0) {
            $result->diffState = "different";
            return $result;
        }

        $result->diffState = "ok";
        return $result;
    }
}
