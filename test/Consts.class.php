<?php
$APP_CONSTS = 1;

/**
 * Trida pro definici vyctovych hodnot navratovych kodu.
 */
class AppCodes
{
    /*** Skript se ukoncuje uspechem. */
    public const Success = 0;

    /*** Doslo k chybe pri nacitani parametru. Napr. neplatna kombinace. */
    public const InvalidParameters = 10;

    /*** Nedari se otevrit vstupni soubor. Neexistuje, chybejici prava, atd... */
    public const CannotOpenInputFileOrDirectory = 11;
}

const PHP_EXECUTABLE = "php"; // TODO: PHP7.4
const PYTHON_EXECUTABLE = "python3.8";
const JAVA_EXECUTABLE = "java -jar";
const DIFF_EXECUTABLE = "diff";
const DEFAULT_PATH = '.';
const DEFAULT_PARSE = 'parse.php';
const DEFAULT_INT = 'interpret.py';
const DEFAULT_JEXAMXML = '/pub/courses/ipp/jexamxml/jexamxml.jar';
