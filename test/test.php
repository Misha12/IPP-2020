<?php
if (!isset($APP_CODES)) include 'app_codes.php';
if (!isset($ARG_PARSE)) include 'arg_parser.php';
if (!isset($HELPER)) include 'helper.php';

$commandLineParser = new CommandLineArgsParseService();

$args = $commandLineParser->getAndParse();

if ($args->help) {
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

// TODO(DONE): Načítání parametrů příkazové řádky.
// TODO(DONE): Nápověda.
// TODO: Načtení seznamů testů.
// TODO: Registrace testů do kontejneru.
// TODO: Inicializace testů (Kontroly, vytvoření chybějících souborů, atd... Případně zařvat FUCK YOU).
// TODO: Provedení testů.
// TODO: Zpracování výsledků.
// TODO: Generování HTML.