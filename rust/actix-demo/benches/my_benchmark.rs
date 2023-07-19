use criterion::{criterion_group, criterion_main, Criterion};
use hello::ext::err_code;

// pub fn get_map_with_cache_benchmark(c: &mut Criterion) {
//     c.bench_function("user status get_map_with_cache", 
//         |b| b.iter(||  err_code::get_map_once() ));
// }

pub fn get_map_benchmark(c: &mut Criterion) {
    c.bench_function("user status get_map", 
        |b| b.iter(||  err_code::get_map() ));
}

// criterion_group!(benches, get_map_with_cache_benchmark, get_map_benchmark);
criterion_group!(benches, get_map_benchmark);
criterion_main!(benches);