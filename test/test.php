<?php
if (!isset($APP_CONSTS)) include 'Consts.class.php';
if (!isset($ARG_PARSE)) include 'ArgumentParser.class.php';
if (!isset($HELPER)) include 'helper.php';
if (!isset($TEST_LOADER)) include 'TestLoaderService.class.php';
if (!isset($HTML_GENERATOR)) include 'HTMLGenerator.class.php';

// TODO: Možná z toho půjdou udělat static položky. Nebo dokonce funkce.
$commandLineParser = new CommandLineArgsParseService();
$testLoader = new TestsLoaderService();

$config = $commandLineParser->getAndParse();

if ($config->help) {
    output("Testovací skript pro spuštění testů nad analyzátorem a interpreterem kódu IPPCode20." . PHP_EOL);
    output("Test je možno ovlivnit následujícími parametry (Všechny parametry jsou volitelné a mají nastavenou výchozí hodnotu.):");

    output("--help\tOtevře nápovědu.");
    output("--directory={path}\tCesta k testům. Výchozí je './'");
    output("--recursive\tZapnutí vyhledávání testů bude probíhat rekurzivně.");
    output("--parse-script={filepath}\Nastavení cesty k analyzátoru kódu IPPCode20. Cesta musí obsahovat i název souboru. Výchozí je './parse.php'");
    output("--int-script={filepath}\tNastavení cesty k interpreteru kódu IPPCode20. Cesta musí obsahovat i název souboru. Výchozí je './interpret.py'");
    output("--parse-only\tSpuštění testů pouze nad analyzátorem kódu. Nesmí se kombinovat s přepínači --int-script a --int-only.");
    output("--int-only\tSpuštění testů pouze nad interpretací kódu IPPCode20. Nesmí se kombinovat s přepínači --parse-script a --parse-only");
    output("--jexamxml={filepath}\tNastavení cesty k porovnávacímu nástroji jexamxml. Výchozí je (/pub/courses/ipp/jexamxml/jexamlxml.jar). Předpokládá se, že konfigurační soubor bude ve stejném adresáři.");

    output();
    exit(AppCodes::Success);
}

$tests = $testLoader->findTests($config);

$testResults = [];
foreach ($tests as $key => $test) {
    try {
        $test->initTest($config);
        $testResults[$key] = $test->runTest($config);
    } catch (Exception $e) {
        output($e->getMessage());
    }
}

HTMLGenerator::render($testResults, $config);

// TODO(DONE): Načítání parametrů příkazové řádky.
// TODO(DONE): Nápověda.
// TODO(DONE): Načtení testů a jejich registrace do kontejneru.
// TODO(DONE): Inicializace testů (Kontroly, vytvoření chybějících souborů, atd... Případně zařvat FUCK YOU).
// TODO(DONE): Provedení testů (Parser).
// TODO: Provedení testů (Interpret).
// TODO(DONE): Zpracování výsledků.
// TODO(DONE): Generování HTML.
// TODO: Optimalizace. Vyhození nepotřebných položek.

exit(AppCodes::Success);
