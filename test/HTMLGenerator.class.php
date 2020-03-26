<?php
if (!isset($APP_CONSTS)) include 'Consts.class.php';

$HTML_GENERATOR = 1;

class HTMLGenerator
{
    private static $title = "IPP 2020 Výsledky testů";

    public static function render($testResults, $config)
    {
        echo "<!DOCTYPE html><html>";

        self::renderHead();
        self::renderBody($testResults, $config);

        echo "</html>\n";
    }

    private static function renderHead()
    {
        echo "<head><title>" . self::$title . "</title><meta charset='utf-8' />";

        self::renderStyles();

        echo "</head>";
    }

    private static function renderStyles()
    {
        echo "<style>";

        echo "* { margin: 0; padding: 0 }";
        echo "html { background: whitesmoke }";
        echo "body { box-sizing: border-box; font-family: \"Segoe UI\", Arial, \"Noto Sans\", sans-serif }";

        echo "header { background: #343a40; display: grid; grid-template-columns: max-content auto; color: #f8f9fa }";
        echo "header h1 { padding: 10px; padding-right: 15px; margin-right: 15px; font-weight: 100; border-right: 1px solid; }";
        echo "header .created-at { display: flex; align-items: center; }";

        echo ".summary-container { display: flex; justify-content: center; width: 100%; padding-top: 25px }";
        echo ".summary-item { min-width: 550px; height: 300px; box-shadow: 10px 10px 50px -20px rgba(0,0,0,0.4); border-radius: 15px; }";
        echo ".summary-item:not(:last-child) { margin-right: 20px; }";
        echo ".sumamry-item-footer { font-size: 20px; padding: 10px; color: gray; border-top: 1px solid lightgray; }";
        echo ".summary-item-content { height: 250px; color: rgba(0, 0, 0, 0.9); }";
        echo ".summary-item-content ul { padding: 20px; padding-left: 40px; }";
        echo ".summary-item-content li { padding-top: 5px; }";

        echo ".test-summary-grid { display: grid; grid-template-columns: 40% auto; padding: 20px; padding-left: 40px; height: 80%; }";
        echo ".test-summary-grid h1 { font-size: 80px; font-weight: 300; height: 100%; display: flex; align-items: center; grid-column: 1/1; }";
        echo ".test-summary-grid h1.bad, .test-result-status.failed { color: red; }";
        echo ".test-summary-grid h1.middle { color: orange; }";
        echo ".test-summary-grid h1.good, .test-result-status.success { color: green; }";
        echo ".test-summary-grid div { display: flex; align-items: center; grid-column: 2/2; font-weight: 400; }";
        echo ".test-summary-grid div table { width: 100%; }";
        echo ".test-summary-grid div table tr td { font-size: 20px; }";

        echo ".table-results { margin-left: auto; margin-right: auto; width: 70%; }";
        echo ".table-results h1 { margin-top: 50px; margin-bottom: 20px; font-weight: 300; text-align: center; color: rgba(0, 0, 0, 0.7); font-size: 35px; }";
        echo ".table-results-container { box-shadow: 10px 10px 50px -20px rgba(0, 0, 0, 0.4); border-top-left-radius: 15px; border-top-right-radius: 15px; border-bottom-left-radius: 15px; border-bottom-right-radius: 15px; }";

        echo ".test-result { display: flex; border-bottom: 1px solid rgba(81, 85, 90, 0.1); padding: 10px; align-items: center; }";
        echo ".test-result:last-child { border-bottom: none; margin-bottom: 20px; }";
        echo ".test-result-order { border: 1px solid; border-radius: 50%; min-width: 32px; min-height: 32px; font-weight: bold; display: flex; justify-content: center; align-items: center; flex-shrink: 0; margin-right: 16px; }";
        echo ".test-result-columns { display: flex; justify-content: space-between; width: 100%; align-items: center; }";
        echo ".test-result-columns div { padding: 0px 5px; }";
        echo ".test-result-columns div:first-child { width: 100%; }";
        echo ".test-result-columns table { width: 60%; }";
        echo ".test-result-columns table tr th { text-align: left; }";
        echo ".test-result-status { font-weight: 400; }";
        echo ".test-result-table-error-text td { padding-top: 10px; }";

        echo "</style>";
    }

    private static function renderBody($testResults, $config)
    {
        echo "<body>";

        self::renderHeader($testResults, $config);
        self::renderTestsTable($testResults);

        echo "</body>";
    }

    private static function renderHeader($testResults, $config)
    {
        echo "<header><h1>" . self::$title . "</h1> <div class='created-at'>Vytvořeno:<br>" . date("d. m. Y H:i:s") . "</div></header>";
        self::renderSubheader($testResults, $config);
    }

    private static function renderSubheader($testsResult, $config)
    {
        echo "<section class='summary-container'>";

        self::renderConfigCard($config);
        self::renderStatusCard($testsResult);

        echo "</section>";
    }

    /**
     * Vygenerovani karty s konfiguraci testu.
     *
     * @param CommandLineArguments $config
     * @return void
     */
    private static function renderConfigCard($config)
    {
        echo "<div class='summary-item'><div class='summary-item-content'><ul>";
        echo "<li>Adresář: <b>" . $config->directory . "</b></li>";

        if ($config->recursive) echo "<li>Rekurzivní prohledávání</li>";
        if ($config->parseOnly) echo "<li>Pouze parse</li>";
        if ($config->intOnly) echo "<li>Pouze interpret</li>";

        echo "</ul></div><div class='sumamry-item-footer'>Konfigurace testů</div></div>";
    }

    private static function renderStatusCard($testsResult)
    {
        list($success, $failed) = self::computeTestsSummary($testsResult);
        $total = $success + $failed;
        $percentage = round(($success / $total) * 100);
        $result_state = $percentage < 40 ? 'bad' : ($percentage >= 40 && $percentage < 80 ? 'middle' : 'good');

        echo "<div class='summary-item'><div class='summary-item-content'><div class='test-summary-grid'>";
        echo "<h1 class='$result_state'>$percentage%</h1><div><table>";

        echo "<tr><td>Úspěšných:</td><td>$success</td></tr>";
        echo "<tr><td>Neúspěšných:</td><td>$failed</td></tr>";
        echo "<tr><td>Celkem:</td><td>$total</td></tr>";

        echo "</table></div></div></div><div class='sumamry-item-footer'>Souhrn testování</div></div>";
    }

    /**
     * Vypocet statistik uspesnosti testu.
     *
     * @param TestPartResult $testsResult
     * @return void
     */
    private static function computeTestsSummary($testsResult)
    {
        $result = [0, 0];

        foreach ($testsResult as $test) {
            $result[$test->isOk() ? 0 : 1]++;
        }

        return $result;
    }

    private static function renderTestsTable($testResults)
    {
        echo "<section class='table-results'><h1>Výsledky jednotlivých testů</h1><div class='table-results-container'>";

        $keys = array_keys($testResults);
        for ($i = 0; $i < count($keys); $i++) {
            $section = dirname($keys[$i]);
            $testName = basename($keys[$i]);

            $test = $testResults[$keys[$i]];
            $success = $test->isOk();

            echo "<div class='test-result'><div class='test-result-order'>" . ($i + 1) . "</div><div class='test-result-columns'>";
            echo "<div class='test-result-data'><table><tr><th>Sekce: </th><td>$section</td></tr><tr><th>Test:</th><td>$testName</td></tr>";

            if (!$success)
                echo "<tr class='test-result-table-error-text'><td colspan='2'>" . $test->getMessage() . "</td></tr>";

            echo "</table></div><h2 class='test-result-status " . ($success ? 'success' : 'failed') . "'>" . ($success ? 'Úspěch' : 'Selhalo') . "</h2></div></div>";
        }

        echo "</div></section>";
    }
}
