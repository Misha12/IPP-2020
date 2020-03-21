<?php
$HELPER = 1;

class Helper
{
    /**
     * Detekce, zda je retezec prefixem jineho retezce.
     *
     * @param string $str Retezec, ve kterem se ma prefix vyhledavat.
     * @param string $search Predpokladany prefix.
     * @return bool True, pokud byl predpokladany prefix skutecne prefixem.
     */
    public static function startsWith($str, $search)
    {
        return (substr($str, 0, strlen($search)) === $search);
    }

    /**
     * Funkce k ukonceni aplikace z duvodu chyby.
     *
     * @param int $code Ciselny kod chyby.
     * @param string $message Zprava, ktera ma byt vypsana na standardni chybovy vystup. 
     * @return void
     * 
     * @see app_codes.php Ciselnik chybovych kodu.
     */
    public static function errorExit($code, $message = null)
    {
        fwrite(STDERR, "Error $code\n");

        if (!empty($message)) {
            fwrite(STDERR, "$message\n");
        }

        exit($code);
    }
}
