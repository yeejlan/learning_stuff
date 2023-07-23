use serde::{Serialize, Deserialize, ser::SerializeStruct};

#[derive(Deserialize, Debug)]
#[serde(crate = "rocket::serde")]
pub struct User {
    pub id: i64,
    pub name: String,
    pub email: String,
    pub password: String,
    pub status: i32,
}

impl Serialize for User {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        let mut state = serializer.serialize_struct("User", 6)?;
        state.serialize_field("id", &self.id)?;
        state.serialize_field("name", &self.name)?;
        state.serialize_field("email", &self.email)?;
        state.serialize_field("password", &self.password)?;
        state.serialize_field("status", &self.status)?;
        state.serialize_field("status_str", &status::to_str(self.status))?;
        state.end()
    }
}

#[allow(non_upper_case_globals)]
pub mod status {
    use std::collections::BTreeMap;
    use once_cell::sync::Lazy;

    static MAP: Lazy<BTreeMap<i32, &'static str>> = Lazy::new(|| {
        get_map()
    });
    
    static MAP_REVERSED: Lazy<BTreeMap<&'static str, i32>> = Lazy::new(|| {
        let mut m = BTreeMap::new();
        for v in get_map() {
            m.insert(v.1, v.0);
        };
        m
    });

    pub const Normal: i32 = 1;
    pub const Active: i32 = 2;
    pub const Frozen: i32 = 3;
    pub const Closed: i32 = 4;

    pub fn get_map() -> BTreeMap<i32, &'static str> {
        BTreeMap::from([
            (Normal, "normal"),
            (Active, "active"),
            (Frozen, "frozen"),
            (Closed, "closed"),
        ])
    }

    pub fn from_str(value: &str) -> Option<i32> {
        MAP_REVERSED.get(value)
        .copied()
    }

    pub fn to_str(value: i32)-> Option<&'static str> {
        MAP.get(&value)
        .copied()
    }
}
