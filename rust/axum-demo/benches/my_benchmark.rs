use std::collections::{BTreeMap, HashMap};

use criterion::{criterion_group, criterion_main, Criterion};
use once_cell::sync::Lazy;
use cached::proc_macro::once;

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

pub fn b_get_map_cached(c: &mut Criterion) {
    c.bench_function("b_get_map_cached", 
        |b| b.iter(||  get_map_cached() ));
}



static MAP: Lazy<BTreeMap<i32, String>> = Lazy::new(|| {
    get_map()
});

fn get_map_static() -> &'static BTreeMap<i32, String> {
    &MAP
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
fn get_map_cached() -> BTreeMap<i32, String> {
    get_map()
}

// criterion_group!(benches, get_map_with_cache_benchmark, get_map_benchmark);
criterion_group!(benches, b_get_map_static, b_get_map, b_get_map_cached);
criterion_main!(benches);
