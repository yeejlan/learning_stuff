use std::collections::BTreeMap;
use cached::proc_macro::once;

//error kind
pub const USER_EXCEPTION: i32 = -1000;
pub const MODEL_EXCEPTION: i32 = -2000;
pub const SERVICE_EXCEPTION: i32 = -3000;
pub const FLUX_EXCEPTION: i32 = -4000;

//error code
pub const SUCCESS: i32 = 0;
pub const BAD_RESULT: i32 = 1000;
pub const BAD_TOKEN: i32 = 1100;
pub const BAD_PARAM: i32 = 1200;
pub const OPERATION_NOT_ALLOWED: i32 = 1300;
pub const RESOURCE_NOT_FOUND: i32 = 1400;
pub const OPERATION_FAILED: i32 = 1500;
pub const OPERATION_PENDING: i32 = 1600;


#[once]
pub fn get_map() -> BTreeMap<i32, &'static str> {
    BTreeMap::from([
        (401, "unauthorized"),
        (403, "forbidden"),
        (404, "not_found"),
        (405, "method_not_allowed"),
        (500, "internal_server_error"),

        (SUCCESS, "success"),
        (BAD_RESULT, "bad_result"),
        (BAD_TOKEN, "bad_token"),
        (BAD_PARAM, "bad_param"),
        (OPERATION_NOT_ALLOWED, "operation_not_allowed"),
        (RESOURCE_NOT_FOUND, "resource_not_found"),
        (OPERATION_FAILED, "operation_failed"),
        (OPERATION_PENDING, "operation_pending"),
    ])
}

pub fn to_str(code: i32) -> &'static str {
    let m = get_map();
    m.get(&code).unwrap_or(&"none")
}

pub fn kind(code: i32) -> i32 {
    if code >= 1000 {
        return USER_EXCEPTION;
    }
    code - (code % 1000)
}
