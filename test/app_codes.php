<?php
$APP_CODES = 1;

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
