use crate::debug;
use crate::token::Token;
use crate::token_type::TokenType;

pub fn match_heading(text: &str, mut i: usize, mut line: usize, tokens: &mut Vec<Token>) -> (usize, usize) {
    let mut heading: String = String::new();
    let mut h_count: usize = 0;

    loop {
        let c = &text[i..=i];

        match c {
            "#" => {
                h_count += 1;
                heading += c;
            }
            _ => break,
        }
        i += 1;
    }

    if h_count > 6 {
        debug::warn(format!("Line: {}, Index: {} -> Too many #! Heading only go up to 6!", line, i).as_str());
        tokens.push(Token::new(TokenType::Error as usize, i - (h_count - 1) - 1, i, heading));

        return (i, line);
    }

    tokens.push(Token::new(TokenType::Heading as usize, i - (h_count - 1) - 1, i, heading,));
    tokens.push(Token::new_space(i));
    i += 1;

    let mut heading_text: String = String::new();
    let start: usize = i;
    loop {
        let c = &text[i..=i];

        match c {
            "\n" => {
                line += 1;
                tokens.push(Token::new(TokenType::HeadingText as usize, start, i, heading_text));
                tokens.push(Token::empty(TokenType::HeadingEnd as usize));
                break;
            }
            _ => heading_text += c,
        }
        i += 1;
    }

    (i, line)
}

pub fn match_bold(text: &str, mut i: usize, line: usize, tokens: &mut Vec<Token>) -> (usize, usize) {
    tokens.push(Token::new_double(TokenType::BoldBegin as usize, i - 1, String::from("**")));
    i += 1;
    let mut matched_text: String = String::new();

    let start: usize = i;
    loop {
        let c = &text[i..=i];

        match c {
            "*" => {
                i += 1;
                let next_c = &text[i..=i];
                match next_c {
                    "*" => {
                        tokens.push(Token::new(TokenType::Bold as usize, start, i - 1, matched_text));
                        tokens.push(Token::new_double(TokenType::BoldEnd as usize, i - 1, String::from("**")));
                        break;
                    }
                    _ => break,
                }
            }
            _ => matched_text += c,
        }
        i += 1;
    }

    (i, line)
}

pub fn match_italic(text: &str, mut i: usize, line: usize, tokens: &mut Vec<Token>) -> (usize, usize) {
    tokens.push(Token::new_single(TokenType::ItalicBegin as usize, i - 1, String::from("*")));
    let mut matched_text: String = String::new();

    let start: usize = i;
    loop {
        let c = &text[i..=i];

        match c {
            "*" => {
                tokens.push(Token::new(TokenType::Italic as usize, start, i, matched_text));
                tokens.push(Token::new_single(TokenType::ItalicEnd as usize, i, String::from("*")));
                break;
            }
            _ => matched_text += c,
        }

        i += 1;
    }

    (i, line)
}