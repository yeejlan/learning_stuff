import ope_init as _
from ope_thread_pool import pool
from ope_tracing import *
from ope_exception import *
from ope_reply import *

def json_decode(str_data: str): 

    try:
        data = json.loads(str_data)
    except json.JSONDecodeError as e:
        error_str = f"JSON Decode Error: {e.msg} on line {e.lineno}, column {e.colno}"        
        raise UserException(error_str, BAD_RESULT)

    return data