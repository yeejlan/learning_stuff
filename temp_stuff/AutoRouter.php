<?php

namespace App\Http;

use App\Exceptions\UserException;
use Illuminate\Contracts\Routing\Registrar as RegistrarContract;
use Illuminate\Contracts\Routing\BindingRegistrar;
use Illuminate\Http\Response;
use Illuminate\Routing\Router;

class AutoRouter extends Router implements BindingRegistrar, RegistrarContract {

    protected function findRoute($request)
    {
        $uri = $request->path();
        $module = $controller = $action = '';

        if($uri == '/') {
            $routePath = 'App\Http\Controllers\HomeController@indexAction';
            return $this->generateAutoRoute($request, $routePath, [
                'module' => '',
                'controller' => 'HomeController',
                'action' => 'indexAction',
            ]);
        }

        $uriArr = explode('/', $uri);
        if(count($uriArr) == 3) {
            $module = $uriArr[0];
            $controller = $uriArr[1];
            $action = $uriArr[2];
        }elseif(count($uriArr) == 2) {
            $module = '';
            $controller = $uriArr[0];
            $action = $uriArr[1];
        }else {
            abort(404);
        }

        $module = ucfirst($module);
        $controllerArr = array_map('ucfirst', explode('-', $controller));
        $controller = implode('', $controllerArr);
        $controller .= 'Controller';
        $actionArr = array_map('ucfirst', explode('-', $action));
        $action = implode('', $actionArr);
        $action .= 'Action';
        $action = lcfirst($action);

        if($module) {
            $className = 'App\\Http\\Controllers\\' . $module . '\\' . $controller;
        } else {
            $className = 'App\\Http\\Controllers\\' . $controller;
        }

        try{
            $class = app()->make($className);
        }catch(Illuminate\Contracts\Container\BindingResolutionException $e){
            //class not existed.
            abort(404);
        }

        //action not existed.
        if (!method_exists($class, $action)) {
            abort(404);
        }

        $routePath = $className . '@' . $action;

        return $this->generateAutoRoute($request, $routePath, [
            'module' => $module,
            'controller' => $controller,
            'action' => $action,
        ]);
    }

    private function generateAutoRoute($request, $routePath, $routeParams = []) {

        $method = $request->method();
        if($method != 'OPTIONS' && $method != 'GET' && $method != 'POST') {
            throw new UserException('Method not allowed', 405);
        }

        $uri = $request->path();

        if($method == 'OPTIONS') {
            $this->current = $route = $this->newRoute(['OPTIONS'], $uri, function(){
                return new Response('', 204);
            });
        } else {
            $this->current = $route = $this->newRoute(['GET', 'POST', 'HEAD'], $uri, [
                'middleware' => ['web'],
                'uses' => $routePath,
                'controller' => $routePath,
            ]);
        }

        $route->bind($request);

        if($routeParams) {
            foreach($routeParams as $key => $value) {
                $route->setParameter($key, $value);
            }
        }

        $route->setContainer($this->container);

        $this->container->instance(Route::class, $route);

        return $route;
    }
}
