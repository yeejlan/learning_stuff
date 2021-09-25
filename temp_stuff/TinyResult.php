<?php

class TinyResult
{
    private $data;
    private array $cause;
    private $error;
    private static $logger;
    public function __construct($error, $data)
    {
        $this->error = $error;
        $this->cause = [];
        $this->data = $data;
        if($error){
            $this->_addCause($error);
            if($data){
                if($data instanceof self){
                    $this->cause = array_merge($this->cause, $data->getCause());
                }else if(is_array($data)){
                    $this->cause = array_merge($this->cause, $data);
                }else{
                    $this->cause[] = $data.'';
                }
            }
        }
    }

    public static function setLogger($logger)
    {
        self::$logger = $logger;
    }

    public function error()
    {
        if($this->error){
            return $this->error;
        }
        return false;
    }

    public function data()
    {
        if($this->error){
            if(self::$logger){
                self::$logger->log($this->error.'; '.$this->cause());
            }
            throw new TinyResultException('Bad result: '.$this->cause());
        }
        return $this->data;
    }

    public function cause(): string
    {
        return join('; ', $this->cause);
    }

    public function getCause(): array
    {
        return $this->cause;
    }

    public function __toString(): string
    {
        return $this->cause();
    }

    private function _addCause($cause)
    {
        $e = new \Exception;
        $traceArr = $e->getTrace();
        foreach ($traceArr as $trace){
            if(isset($trace['function'], $trace['class'])) {
                if ($trace['function'] == '__construct' && $trace['class'] == self::class) {
                    $file = basename($trace['file']);
                    $line = $trace['line'];
                    $message = "$cause@$file:$line";
                    $this->cause[] = $message;
                    break;
                }
            }
        }
    }
}

class TinyResultException extends \Exception{}