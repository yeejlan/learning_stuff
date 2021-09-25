<?php

require "./TinyResult.php";

function foo(){
    try{
        bar();
    }catch(\Exception $e){
        $tr = new TinyResult('bad result', $e);
        print_r($tr->getCause());
    }

    echo '~~~~~~',PHP_EOL;
    try{
        $tr = new TinyResult('db error', null);
        $tr->data();
    }catch(\Exception $e){
        $tr = new TinyResult('got some error', $e);
        print_r($tr->getCause());
    }
    echo '~~~~~~',PHP_EOL;
    $tr = new TinyResult('error chain', ['my error description','more detail']);
    $tr2 = new TinyResult('error chain 2',  $tr);
    print_r($tr2->getCause());
}

function bar(){
    $tr = new TinyResult('my error', 'my error description');
    print_r($tr->getCause());
    echo '~~~~~~',PHP_EOL;
    throw new \Exception('somthing happened');
}

foo();