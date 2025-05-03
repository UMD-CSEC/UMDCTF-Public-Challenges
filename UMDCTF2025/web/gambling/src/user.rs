use std::net::IpAddr;
use std::sync::atomic::{AtomicI32, Ordering};
use std::sync::{Arc, Mutex, RwLock};

pub struct User {
    pub username: String,
    pub password: String,
    pub credits: AtomicI32,
    pub signup_ip: IpAddr,
    pub ratelimited_ips: Mutex<Vec<IpAddr>>,
}

impl User {
    pub fn new(username: String, password: String, signup_ip: IpAddr) -> Self {
        Self {
            username,
            password,
            credits: AtomicI32::new(0),
            signup_ip,
            ratelimited_ips: Mutex::new(Vec::new()),
        }
    }

    pub fn test_ratelimited(&self, ip: IpAddr) -> bool {
        let mut ratelimited_ips = self.ratelimited_ips.lock().unwrap();
        let is_ratelimited = ratelimited_ips.contains(&ip);
        if !is_ratelimited {
            ratelimited_ips.push(ip);
        }

        is_ratelimited
    }

    pub fn use_credits(&self, credits_to_use: i32, allow_negative: bool) -> bool {
        self.credits
            .fetch_update(Ordering::SeqCst, Ordering::SeqCst, |old_credits| {
                let new_credits = old_credits - credits_to_use;
                let valid = if allow_negative {
                    new_credits >= -100
                } else {
                    new_credits >= 0
                };

                if valid {
                    Some(new_credits)
                } else {
                    None
                }
            })
            .is_ok()
    }
}

pub struct UserDatabase {
    users: RwLock<Vec<Arc<User>>>,
}

impl UserDatabase {
    pub fn new() -> UserDatabase {
        Self {
            users: RwLock::new(Vec::new()),
        }
    }

    pub fn create_user(&self, user: User) -> bool {
        let mut users_guard = self.users.write().unwrap();
        if users_guard
            .iter()
            .any(|existing_user| existing_user.username == user.username)
        {
            return false;
        }

        users_guard.push(Arc::new(user));
        true
    }

    pub fn find_user(&self, username: &str, password: &str) -> Option<Arc<User>> {
        let users_guard = self.users.read().unwrap();
        users_guard
            .iter()
            .find(|user| user.username == username && user.password == password)
            .cloned()
    }

    pub fn reset(&self) {
        let mut users_guard = self.users.write().unwrap();
        users_guard.clear();
    }
}
