import spy;
import threading

request_context = threading.local()

def set_request_id(request_id: str) -> None:
    request_context.request_id = request_id

def get_request_id() -> str:
    request_id = "0000"
    try:
        request_id = request_context.request_id
    except AttributeError: 
        pass

    return request_id

def del_request_id() -> None:
    del request_context.request_id

def debug(msg: str, context: dict = {}) -> None:
    context['request-id'] = get_request_id()
    spy.tracing_debug(f"{msg} {context}")

def info(msg: str, context: dict = {}) -> None:
    context['request-id'] = get_request_id()
    spy.tracing_info(f"{msg} {context}")

def warn(msg: str, context: dict = {}) -> None:
    context['request-id'] = get_request_id()
    spy.tracing_warn(f"{msg} {context}")

def error(msg: str, context: dict = {}) -> None:
    context['request-id'] = get_request_id()
    spy.tracing_error(f"{msg} {context}")
