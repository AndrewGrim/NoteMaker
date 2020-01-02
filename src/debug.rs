#![allow(dead_code)]
pub fn info(text: &str) {
    let color = "\x1b[94m";
    let end = "\x1b[0m";
    println!("{}{}{}", color, text, end);
}

pub fn ok(text: &str) {
    let color = "\x1b[96m";
    let end = "\x1b[0m";
    println!("{}{}{}", color, text, end);
}

pub fn success(text: &str) {
    let color = "\x1b[92m";
    let end = "\x1b[0m";
    println!("{}{}{}", color, text, end);
}

pub fn debug(text: &str) {
    let color = "\x1b[95m";
    let end = "\x1b[0m";
    println!("{}{}{}", color, text, end);
}

pub fn warn(text: &str) {
    let color = "\x1b[93m";
    let end = "\x1b[0m";
    println!("{}{}{}", color, text, end);
}

pub fn fail(text: &str) {
    let color = "\x1b[91m";
    let end = "\x1b[0m";
    println!("{}{}{}", color, text, end);
}

pub fn test() {
    ok("ok()");
    info("info()");
    success("success()");
    debug("debug()");
    warn("warn()");
    fail("fail()");
}
