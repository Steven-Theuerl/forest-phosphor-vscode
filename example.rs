// example.rs — theme conflict testing: Rust
// Focus: trait impls, lifetimes, generics, macros, enums, pattern matching

use std::collections::HashMap;
use std::fmt;
use std::sync::{Arc, Mutex};

// ─── Constants ────────────────────────────────────────────────────────────────

const MAX_CONNECTIONS: usize = 100;
const DEFAULT_TIMEOUT: u64   = 5_000;
const VERSION: &str          = env!("CARGO_PKG_VERSION");

// ─── Macros ───────────────────────────────────────────────────────────────────

macro_rules! bail {
    ($msg:literal $(,)?) => {
        return Err(AppError::new($msg))
    };
    ($fmt:expr, $($arg:tt)*) => {
        return Err(AppError::new(format!($fmt, $($arg)*)))
    };
}

macro_rules! map {
    ($($k:expr => $v:expr),* $(,)?) => {{
        let mut m = HashMap::new();
        $( m.insert($k, $v); )*
        m
    }};
}

// ─── Error type ───────────────────────────────────────────────────────────────

#[derive(Debug, Clone)]
pub struct AppError {
    message: String,
    code:    u32,
}

impl AppError {
    pub fn new(message: impl Into<String>) -> Self {
        Self { message: message.into(), code: 0 }
    }

    pub fn with_code(mut self, code: u32) -> Self {
        self.code = code;
        self
    }
}

impl fmt::Display for AppError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "[{}] {}", self.code, self.message)
    }
}

impl std::error::Error for AppError {}

type Result<T> = std::result::Result<T, AppError>;

// ─── Enums ────────────────────────────────────────────────────────────────────

#[derive(Debug, Clone, PartialEq)]
pub enum UserRole {
    Admin,
    Editor { department: String },
    Viewer,
}

impl fmt::Display for UserRole {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            UserRole::Admin                  => write!(f, "admin"),
            UserRole::Editor { department }  => write!(f, "editor:{}", department),
            UserRole::Viewer                 => write!(f, "viewer"),
        }
    }
}

#[derive(Debug, Clone)]
pub enum Event {
    UserCreated(User),
    UserUpdated { id: u64, changes: Vec<String> },
    UserDeleted(u64),
    Heartbeat,
}

// ─── Structs ─────────────────────────────────────────────────────────────────

#[derive(Debug, Clone)]
pub struct User {
    pub id:       u64,
    pub username: String,
    pub email:    String,
    pub role:     UserRole,
    pub profile:  UserProfile,
    pub settings: UserSettings,
}

#[derive(Debug, Clone, Default)]
pub struct UserProfile {
    pub display_name: String,
    pub avatar_url:   Option<String>,
    pub bio:          String,
    pub social:       SocialLinks,
}

#[derive(Debug, Clone, Default)]
pub struct SocialLinks {
    pub twitter: Option<String>,
    pub github:  Option<String>,
    pub website: Option<String>,
}

#[derive(Debug, Clone)]
pub struct UserSettings {
    pub theme:         Theme,
    pub notifications: bool,
    pub language:      String,
}

#[derive(Debug, Clone, PartialEq)]
pub enum Theme { Light, Dark, System }

impl Default for UserSettings {
    fn default() -> Self {
        Self {
            theme:         Theme::Dark,
            notifications: true,
            language:      String::from("en"),
        }
    }
}

// ─── Traits ──────────────────────────────────────────────────────────────────

pub trait Describable {
    fn describe(&self) -> String;
    fn short_desc(&self) -> String {
        let full = self.describe();
        full.chars().take(64).collect()
    }
}

pub trait Validate {
    fn validate(&self) -> Result<()>;
}

pub trait Repository<T, Id> {
    fn find(&self, id: Id)          -> Option<&T>;
    fn save(&mut self, item: T)     -> Result<Id>;
    fn delete(&mut self, id: Id)    -> Result<()>;
    fn all(&self)                   -> Vec<&T>;
}

// ─── Trait Implementations ───────────────────────────────────────────────────

impl Describable for User {
    fn describe(&self) -> String {
        // property.field.field chain for theme testing ↓
        let handle  = self.profile.social.twitter
            .as_deref()
            .unwrap_or(&self.username);
        let website = self.profile.social.website
            .as_deref()
            .unwrap_or("(none)");
        format!(
            "{} (@{}) [{}] — {}",
            self.profile.display_name, handle, self.role, website
        )
    }
}

impl Validate for User {
    fn validate(&self) -> Result<()> {
        if self.username.is_empty()   { bail!("username cannot be empty"); }
        if self.email.is_empty()      { bail!("email cannot be empty"); }
        if !self.email.contains('@')  { bail!("invalid email: {}", self.email); }
        Ok(())
    }
}

// ─── Generic Repository ──────────────────────────────────────────────────────

pub struct InMemoryRepo<T> {
    store:   HashMap<u64, T>,
    next_id: u64,
}

impl<T: Clone> InMemoryRepo<T> {
    pub fn new() -> Self {
        Self { store: HashMap::new(), next_id: 1 }
    }
}

impl<T: Clone> Repository<T, u64> for InMemoryRepo<T> {
    fn find(&self, id: u64) -> Option<&T> {
        self.store.get(&id)
    }

    fn save(&mut self, item: T) -> Result<u64> {
        let id = self.next_id;
        self.store.insert(id, item);
        self.next_id += 1;
        Ok(id)
    }

    fn delete(&mut self, id: u64) -> Result<()> {
        self.store.remove(&id).ok_or_else(|| AppError::new("not found"))?;
        Ok(())
    }

    fn all(&self) -> Vec<&T> {
        self.store.values().collect()
    }
}

// ─── Lifetimes ───────────────────────────────────────────────────────────────

pub struct Paginated<'a, T> {
    items:   &'a [T],
    page:    usize,
    per_page: usize,
}

impl<'a, T> Paginated<'a, T> {
    pub fn new(items: &'a [T], page: usize, per_page: usize) -> Self {
        Self { items, page, per_page }
    }

    pub fn current_page(&self) -> &'a [T] {
        let start = (self.page - 1) * self.per_page;
        let end   = (start + self.per_page).min(self.items.len());
        &self.items[start..end]
    }

    pub fn total_pages(&self) -> usize {
        (self.items.len() + self.per_page - 1) / self.per_page
    }
}

// ─── Arc / Mutex shared state ────────────────────────────────────────────────

pub struct EventBus {
    listeners: Arc<Mutex<Vec<Box<dyn Fn(&Event) + Send + Sync>>>>,
}

impl EventBus {
    pub fn new() -> Self {
        Self { listeners: Arc::new(Mutex::new(Vec::new())) }
    }

    pub fn subscribe(&self, f: impl Fn(&Event) + Send + Sync + 'static) {
        self.listeners.lock().unwrap().push(Box::new(f));
    }

    pub fn publish(&self, event: &Event) {
        for listener in self.listeners.lock().unwrap().iter() {
            listener(event);
        }
    }
}

// ─── Iterators & Closures ────────────────────────────────────────────────────

fn filter_admins(users: &[User]) -> Vec<&User> {
    users.iter()
        .filter(|u| u.role == UserRole::Admin)
        .collect()
}

fn sort_by_name(users: &mut Vec<User>) {
    users.sort_by(|a, b| {
        a.profile.display_name.cmp(&b.profile.display_name)
    });
}

fn word_frequency(text: &str) -> HashMap<&str, usize> {
    text.split_whitespace()
        .fold(HashMap::new(), |mut acc, word| {
            *acc.entry(word).or_insert(0) += 1;
            acc
        })
}

// ─── Pattern Matching ────────────────────────────────────────────────────────

fn handle_event(event: &Event) -> String {
    match event {
        Event::UserCreated(user) => {
            format!("Created: {}", user.describe())
        }
        Event::UserUpdated { id, changes } if changes.is_empty() => {
            format!("Updated user #{id} (no changes)")
        }
        Event::UserUpdated { id, changes } => {
            format!("Updated user #{id}: {}", changes.join(", "))
        }
        Event::UserDeleted(id) => format!("Deleted user #{id}"),
        Event::Heartbeat       => String::from("♥"),
    }
}

fn role_permissions(role: &UserRole) -> &'static [&'static str] {
    match role {
        UserRole::Admin                  => &["read", "write", "delete", "admin"],
        UserRole::Editor { .. }          => &["read", "write"],
        UserRole::Viewer                 => &["read"],
    }
}

// ─── Builder pattern ─────────────────────────────────────────────────────────

#[derive(Default)]
pub struct UserBuilder {
    username: String,
    email:    String,
    role:     Option<UserRole>,
    profile:  Option<UserProfile>,
}

impl UserBuilder {
    pub fn new(username: impl Into<String>, email: impl Into<String>) -> Self {
        Self { username: username.into(), email: email.into(), ..Default::default() }
    }

    pub fn role(mut self, role: UserRole) -> Self {
        self.role = Some(role);
        self
    }

    pub fn profile(mut self, profile: UserProfile) -> Self {
        self.profile = Some(profile);
        self
    }

    pub fn build(self) -> Result<User> {
        let user = User {
            id:       0,
            username: self.username,
            email:    self.email,
            role:     self.role.unwrap_or(UserRole::Viewer),
            profile:  self.profile.unwrap_or_default(),
            settings: UserSettings::default(),
        };
        user.validate()?;
        Ok(user)
    }
}

// ─── Main ────────────────────────────────────────────────────────────────────

fn main() -> Result<()> {
    println!("Forest Phosphor theme test — Rust v{}", VERSION);
    println!("max_connections={MAX_CONNECTIONS}, timeout={DEFAULT_TIMEOUT}ms");

    let mut repo: InMemoryRepo<User> = InMemoryRepo::new();

    let alice = UserBuilder::new("alice", "alice@example.com")
        .role(UserRole::Admin)
        .profile(UserProfile {
            display_name: String::from("Alice Forester"),
            social: SocialLinks {
                github:  Some(String::from("alice-dev")),
                twitter: Some(String::from("@alice")),
                website: None,
            },
            ..Default::default()
        })
        .build()?;

    let bob = UserBuilder::new("bob", "bob@example.com")
        .role(UserRole::Editor { department: String::from("content") })
        .build()?;

    let alice_id = repo.save(alice)?;
    let _bob_id  = repo.save(bob)?;

    let users: Vec<&User> = repo.all();
    let bus               = EventBus::new();

    bus.subscribe(|e| println!("EVENT: {}", handle_event(e)));

    if let Some(alice) = repo.find(alice_id) {
        println!("{}", alice.describe());
        println!("Permissions: {:?}", role_permissions(&alice.role));
        bus.publish(&Event::UserCreated(alice.clone()));
    }

    let mut owned: Vec<User> = users.into_iter().cloned().collect();
    sort_by_name(&mut owned);

    let admins = filter_admins(&owned);
    println!("Admins: {}", admins.len());

    let paginated = Paginated::new(&owned, 1, 5);
    println!("Page 1/{}: {} items", paginated.total_pages(), paginated.current_page().len());

    let freq = word_frequency("the quick brown fox jumps over the lazy dog the fox");
    println!("'the' appears {} times", freq.get("the").unwrap_or(&0));

    let labels = map! {
        "admin"  => "Administrator",
        "editor" => "Content Editor",
        "viewer" => "Read-Only",
    };
    println!("{:?}", labels);

    Ok(())
}
