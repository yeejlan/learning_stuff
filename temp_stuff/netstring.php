<?php

class NetStringException extends \Exception{};

class NetString {

    const DELIMITER = "\n";
    const ENDING = ',';

    public static function encode($value) {
        $value = json_encode($value);
        $len = strlen($value);
        return $len . self::DELIMITER . $value . self::ENDING;
    }

    public static function decode($netstring, $streaming = false)
    {
        if (!$netstring) {
            throw new NetStringException('Can\'t decode empty string.');
        }
        $len = 0;
        if($streaming) {
            fscanf($netstring, '%9u', $len);
        }else {
            sscanf($netstring, '%9u', $len);
        }
        if($streaming) {
            $recv_len = $len+1;
            $data = '';
            while ($recv_len && !feof($netstring)) {
                $recv = fread($netstring, $recv_len);
                $data .= $recv;
                $recv_len -= strlen($recv);
            }
            if(strlen($data) != $len+1) {
                throw new NetStringException('Read stream error.');
            }
            $paypoad = substr($data, 0, $len);
            $ending = substr($data, -1);
        }else {
            $spos = strlen($len);
            $delimiter = substr($netstring, $spos, 1);
            if($delimiter != self::DELIMITER) {
                throw new NetStringException('Invalid delimiter.');
            }            
            $paypoad = substr($netstring, $spos+1, $len);
            $ending = substr($netstring, -1);
        }

        if($ending != self::ENDING) {
            throw new NetStringException('Invalid ending.');
        }
        return json_decode($paypoad, true);
    }

}


$payload = array(
    'poster' => array(
        array(
            'name'     => 'yee',
            'email'    => 'yee#testing.dev',
            'homepage' => 'https://github.com/yeejlan',
            'hint' => [1.12,234344,3],
        ),
    ),
);

$encoded = NetString::encode($payload);
echo $encoded,PHP_EOL;
$decoded = NetString::decode($encoded);
print_r($decoded);
$stream_encoded = fopen('data://text/plain,' . $encoded, 'r');
$decoded = NetString::decode($stream_encoded, true);
print_r($decoded);

$NNN =5000;

$t1 = microtime(true);
for($i=0;$i<$NNN;$i++){
	$encoded = NetString::encode($payload);
	$decoded = NetString::decode($encoded);
}
$t2 = microtime(true);


echo $t2-$t1,PHP_EOL;

$t1 = microtime(true);
for($i=0;$i<$NNN;$i++){
	$encoded = json_encode($payload);
    $decoded = json_decode($encoded, true);
}
$t2 = microtime(true);

echo $t2-$t1,PHP_EOL;