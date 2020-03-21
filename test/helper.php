<?php
$HELPER = 1;

class Helper
{
    /**
     * Detekce, zda je retezec prefixem jineho retezce.
     *
     * @param string $str
     * @param string $search
     * @return bool
     */
    public static function startsWith($str, $search)
    {
        return (substr($str, 0, strlen($search)) === $search);
    }
}
