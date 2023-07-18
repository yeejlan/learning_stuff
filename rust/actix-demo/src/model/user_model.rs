pub mod status {
    use cached::proc_macro::once;
    use std::collections::BTreeMap;

    use crate::ext::exception::Exception;


    pub const NORMAL: i32 = 1;
    pub const ACTIVE: i32 = 2;
    pub const FROZEN: i32 = 3;
    pub const CLOSED: i32 = 3;

    pub fn get_map() -> BTreeMap<i32, &'static str> {
        BTreeMap::from([
            (NORMAL, "normal"),
            (ACTIVE, "active"),
            (FROZEN, "frozen"),
            (CLOSED, "closed"),
        ])
    }

    #[once]
    pub fn get_map_reversed() -> BTreeMap<&'static str, i32> {
        let mut m: BTreeMap<&str, i32> = BTreeMap::new();
        for v in get_map() {
            m.insert(v.1, v.0);
        };
        m
    }

    pub fn from_str(value: &str) -> Result<i32, Exception> {
        let m = get_map_reversed();
        m.get(value).copied()
        .ok_or_else(|| format!("status not found: {}", value).into())
    }

    pub fn to_str(value: i32)-> &'static str {
        let m = get_map();
        m.get(&value).unwrap()
    }
}