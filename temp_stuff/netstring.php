<?php

class NetStringException extends \Exception{};

class NetString {

	public static function encode($value) {
		$value = json_encode($value);
		$len = strlen($value);
		return $len."\n".$value.',';
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
		if($len > 999999999) {
			throw new NetStringException('Invalid length.');
		}
		if($streaming) {
			$data = fread($netstring, $len+1);
			if(strlen($data) != $len+1) {
				throw new NetStringException('Read stream error.');
			}
			$paypoad = substr($data, 0, $len);
			$ending = substr($data, -1);
		}else {
			$paypoad = substr($netstring, strlen($len)+1, $len);
			$ending = substr($netstring, -1);
		}
		if($ending != ',') {
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