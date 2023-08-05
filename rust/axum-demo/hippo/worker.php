<?php

function handler() {

    $fp = fopen("php://STDIN", 'rb');    
    $buffer = '';
    $needed = 8; // header size 
    
    while($needed > 0) {
      $buffer .= fread($fp, $needed);
      $needed -= strlen($buffer); 
    }

    $header = unpack('N*', $buffer);
    $type = $header[1];
    $length = $header[2];

    // Read payload
    $needed = $length;
    $payload = '';
    
    while($needed > 0 ) {
      $payload .= fread($fp, $needed);
      $needed -= strlen($payload);
    }

    $request = msgpack_unpack($payload);



    echo "got request: ". strlen($payload), PHP_EOL;
    print_r($request);

    throw new \Exception("1123");
}

handler();