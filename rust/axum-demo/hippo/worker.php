<?php
set_time_limit(0);

function handler($in) {

    $buffer = '';
    $needed = 8; // header size 
    
    while($needed > 0 ) {
        $buffer .= fread($in, $needed);
        $needed -= strlen($buffer);
    }

    $header = unpack('N2', $buffer);
    $type = $header[1];
    $length = $header[2];

    // Read payload
    $needed = $length;
    $payload = '';
    
    while($needed > 0 ) {
        $payload .= fread($in, $needed);
        $needed -= strlen($payload);
    }

    $request = json_decode($payload);

    print_r($request);
}

$stdin = fopen("php://STDIN", 'rb');

while(true) {
    ob_start();
    try{
        handler($stdin);
    } catch(\Exception $e) {
        ob_end_clean();
        $out_type = 3;
        $out_msg = (string)$e;
        $out_length = strlen($out_msg);
        $out_header = pack('N2', $out_type, $out_length);
        echo $out_header, $out_msg;
        flush();  
    }

    $out_msg = ob_get_clean();

    $out_type = 2;
    $out_length = strlen($out_msg);
    $out_header = pack('N2', $out_type, $out_length);

    echo $out_header, $out_msg;
    flush();
}