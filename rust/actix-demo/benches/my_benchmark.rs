use std::{sync::Mutex, collections::{BTreeMap, HashMap}};

use criterion::{criterion_group, criterion_main, Criterion};
use hello::ext::err_code;
use once_cell::sync::OnceCell;
use cached::proc_macro::once;

// pub fn get_map_with_cache_benchmark(c: &mut Criterion) {
//     c.bench_function("user status get_map_with_cache", 
//         |b| b.iter(||  err_code::get_map_once() ));
// }

pub fn get_map_benchmark(c: &mut Criterion) {
    c.bench_function("user status get_map", 
        |b| b.iter(||  err_code::get_map() ));
}

pub fn b_get_map_static(c: &mut Criterion) {
    c.bench_function("b_get_map_static", 
        |b| b.iter(||  get_map_static() ));
}

pub fn b_get_map(c: &mut Criterion) {
    c.bench_function("b_get_map", 
        |b| b.iter(||  get_map() ));
}

pub fn b_get_map_as_hashmap(c: &mut Criterion) {
    c.bench_function("b_get_map_as_hashmap", 
        |b| b.iter(||  get_map_as_hashmap() ));
}

pub fn b_get_map_once(c: &mut Criterion) {
    c.bench_function("b_get_map_once", 
        |b| b.iter(||  get_map_once() ));
}


fn get_map_static() -> &'static Mutex<BTreeMap<i32, String>> {
    static INSTANCE: OnceCell<Mutex<BTreeMap<i32, String>>> = OnceCell::new();
    INSTANCE.get_or_init( || {
        let m = get_map();
        Mutex::new(m)
    })
}

fn get_map() -> BTreeMap<i32, String> {
        let m = BTreeMap::from([
            (1, String::from("normal")),
            (2, String::from("active")),
            (3, String::from("frozen")),
            (4, String::from("closed")),
        ]);
        m
}

fn get_map_as_hashmap() -> HashMap<i32, String> {
    let m = HashMap::from([
        (1, String::from("normal")),
        (2, String::from("active")),
        (3, String::from("frozen")),
        (4, String::from("closed")),
    ]);
    m
}

#[once]
fn get_map_once() -> BTreeMap<i32, String> {
    get_map()
}

// criterion_group!(benches, get_map_with_cache_benchmark, get_map_benchmark);
criterion_group!(benches, b_get_map, b_get_map_once, b_get_map_as_hashmap, b_get_map_static);
criterion_main!(benches);
