<?php

function handler() {

    $in = fopen("php://STDIN", 'rb');

    while(true) {

        $buffer = '';
        $needed = 8; // header size 
        
        while($needed > 0) {
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

        $out = var_export($request, true);
        $out_type = 2;
        $out_msg = $payload;
        $out_length = strlen($out_msg);

        $out_header = pack('N2', $out_type, $out_length);

        echo $out_header, $out_msg;
        flush();
    }

}

handler();