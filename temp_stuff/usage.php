<?php

require "./TinyResult.php";

function foo(){
    try{
        bar();
    }catch(\Exception $e){
        $tr = new TinyResult('bad result', $e);
        print_r($tr->getCause());
    }
    $tr = new TinyResult('error chain', 'my error description');
    $tr2 = new TinyResult('error chain 2',  $tr);
    print_r($tr2->getCause());
}

function bar(){
    $tr = new TinyResult('my error', 'my error description');
    print_r($tr->getCause());
    throw new \Exception('somthing happened');
}

foo();
