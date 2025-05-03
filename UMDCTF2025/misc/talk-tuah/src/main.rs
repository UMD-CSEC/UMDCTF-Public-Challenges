use std::{
    collections::HashSet,
    error::Error,
    fs::{self, File},
    io::{Read, Write, stdin},
    os::{linux::fs::MetadataExt, unix::fs::PermissionsExt},
    path::PathBuf,
    sync::LazyLock,
};

use rand::{Rng, distr::Alphanumeric};

const TMP_DIR_RAND_LEN: usize = 24;
static TMP_DIR_PATH: LazyLock<PathBuf> = LazyLock::new(|| {
    let mut p = PathBuf::new();
    p.push("/tmp/talk_tuah");
    let rand: String = rand::rng()
        .sample_iter(&Alphanumeric)
        .take(TMP_DIR_RAND_LEN)
        .map(char::from)
        .collect();
    p.push(rand);
    p
});

unsafe extern "C" {
    fn getuid() -> u32;
    fn getgid() -> u32;
}

fn remember_thought(topic: &str) -> Result<String, Box<dyn Error>> {
    let mut p = PathBuf::new();
    p.push(&*TMP_DIR_PATH);
    p.push(topic);

    // make sure this topic was discussed on the TALK TUAH (R) podcast
    let m = fs::metadata(&p)?;
    let file_uid = m.st_uid();
    let file_gid = m.st_gid();
    let my_uid = unsafe { getuid() };
    let my_gid = unsafe { getgid() };
    if file_uid != my_uid && file_gid != my_gid {
        return Err("you sure we talked about that? not confusing me with someone else?".into());
    }

    println!("hmm, what did you say again??");
    println!("🤔🤔🤔🤔🤔🤔");

    // prevent any symlink talk tuah funny business :))
    let mut f = File::open(&p)?;
    if f.metadata()?.is_symlink() {
        return Err("i smell something fishy going on here".into());
    }
    let mut s = String::new();
    f.read_to_string(&mut s)?;
    Ok(s)
}

fn commit_thoughts(topic: &str, thoughts: &str) -> Result<(), Box<dyn Error>> {
    let mut p = PathBuf::new();
    p.push(&*TMP_DIR_PATH);
    p.push(topic);

    let mut f = File::create_new(&p)?;
    f.write_all(&mut thoughts.as_bytes())?;

    Ok(())
}

fn main() -> Result<(), Box<dyn Error>> {
    let mut topics_discussed = HashSet::new();

    fs::create_dir(&*TMP_DIR_PATH)?;
    fs::set_permissions(&*TMP_DIR_PATH, PermissionsExt::from_mode(0o775))?;
    println!("storage dir: {:?}", *TMP_DIR_PATH);
    println!("");

    println!("thank you for appearing on the TALK TUAH podcast!");
    println!("i'm host haliey welch, and i'm so glad to have you on!");
    println!("");

    loop {
        println!("what topic would you like to TALK TUAHbout: ");

        let mut topic = String::new();
        stdin().read_line(&mut topic)?;
        topic.retain(|c| c.is_ascii_alphanumeric() || c == ' ');

        if topic == "nothing" {
            println!("i look forward to having you on next time!!");
            break;
        }

        if topics_discussed.contains(&topic) {
            println!("u already talk tuahed me about {}!", topic);
            println!("u said {}", remember_thought(&topic)?);
            println!("");
            continue;
        }
        topics_discussed.insert(topic.clone());

        println!(
            "wow, {} is such a good topic! what are your thoughts on {}: ",
            topic, topic
        );
        let mut thoughts = String::new();
        stdin().read_line(&mut thoughts)?;
        thoughts.retain(|c| c.is_ascii_alphanumeric() || c == ' ');

        commit_thoughts(&topic, &thoughts)?;

        println!("wow, so true!!!");
        println!("");
    }

    Ok(())
}
