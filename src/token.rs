use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use pyo3::PyObjectProtocol;

use crate::token_type::TokenType;

#[pyclass]
#[derive(Debug)]
#[derive(PartialEq)]
pub struct NewToken {
    pub id: usize,
    pub begin: usize,
    pub end: usize,
    pub content: String,
}

#[pyclass]
#[derive(Debug)]
#[derive(PartialEq)]
pub struct Token {
    pub id: usize,
    pub begin: usize,
    pub end: usize,
    pub content: String,
    // TODO add html so eliminate the python parser
}

#[pymethods]
impl Token {
    #[getter]
    fn get_id(&self) -> PyResult<u32> {
        Ok(self.id as u32)
    }

    #[setter]
    fn set_id(&mut self, id: usize) -> PyResult<()> {
        self.id = id;
        Ok(())
    }

    #[getter]
    fn get_begin(&self) -> PyResult<u32> {
        Ok(self.begin as u32)
    }

    #[setter]
    fn set_begin(&mut self, begin: usize) -> PyResult<()> {
        self.begin = begin;
        Ok(())
    }

    #[getter]
    fn get_end(&self) -> PyResult<u32> {
        Ok(self.end as u32)
    }

    #[setter]
    fn set_end(&mut self, end: usize) -> PyResult<()> {
        self.end = end;
        Ok(())
    }

    #[getter]
    fn get_content(&self) -> PyResult<&str> {
        Ok(&self.content.as_str())
    }

    #[setter]
    fn set_content(&mut self, content: String) -> PyResult<()> {
        self.content = content;
        Ok(())
    }
}

#[pyproto]
impl PyObjectProtocol for Token {
    fn __str__(&self) -> PyResult<String> {
        Ok(format!(
            "Token {{\n\tid: {}\n\tbegin: {}\n\tend: {}\n\tcontent: '{}'\n}}",
            self.id, self.begin, self.end, self.content
        ))
    }

    fn __repr__(&self) -> PyResult<String> {
        Ok(format!(
            "Token {{\n\tid: {}\n\tbegin: {}\n\tend: {}\n\tcontent: '{}'\n}}",
            self.id, self.begin, self.end, self.content
        ))
    }
}

impl Token {
    pub fn new(id: usize, begin: usize, end: usize, content: String) -> Token {
        Token {
            id,
            begin,
            end,
            content,
        }
    }

    pub fn new_single(id: usize, begin: usize, content: String) -> Token {
        Token {
            id,
            begin,
            end: begin + 1,
            content,
        }
    }

    pub fn new_double(id: usize, begin: usize, content: String) -> Token {
        Token {
            id,
            begin,
            end: begin + 2,
            content,
        }
    }

    pub fn new_tag(id: usize, begin: usize, content: String, tag: &str) -> Token {
        Token {
            id,
            begin,
            end: begin + tag.len(),
            content,
        }
    }

    pub fn space(begin: usize) -> Token {
        Token {
            id: TokenType::Space as usize,
            begin,
            end: begin + 1,
            content: String::from(" "),
        }
    }

    pub fn empty(id: usize) -> Token {
        Token {
            id,
            begin: 0,
            end: 0,
            content: String::new(),
        }
    }
}


#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn new_token() {
        assert_eq!(Token::new(TokenType::Heading as usize, 15, 16, String::from("#")),
            Token {id: TokenType::Heading as usize, begin: 15, end: 16, content: String::from("#")});
    }   

    #[test]
    #[should_panic]
    fn fail_new_token() {
        assert_eq!(Token::new(TokenType::CodeBlockKeyword as usize, 15, 21, String::from("class")),
            Token {id: TokenType::CodeBlockKeyword as usize, begin: 15, end: 20, content: String::from("class")});

        assert_eq!(Token::new(TokenType::CodeBlockKeyword as usize, 15, 21, String::from("class")),
            Token {id: TokenType::CodeBlockKeyword as usize, begin: 15, end: 22, content: String::from("class")});
    }  

    #[test]
    fn new_single_token() {
        assert_eq!(Token::new_single(TokenType::Heading as usize, 15, String::from("#")),
            Token {id: TokenType::Heading as usize, begin: 15, end: 16, content: String::from("#")});
    }

    #[test]
    fn new_double_token() {
        assert_eq!(Token::new_double(TokenType::Heading as usize, 15, String::from("##")),
            Token {id: TokenType::Heading as usize, begin: 15, end: 17, content: String::from("##")});
    }

    #[test]
    fn new_tag_token() {
        assert_eq!(Token::new_tag(TokenType::Heading as usize, 15, String::from("tag"), "tag"),
            Token {id: TokenType::Heading as usize, begin: 15, end: 18, content: String::from("tag")});
    }

    #[test]
    fn new_space_token() {
        assert_eq!(Token::space(15),
            Token {id: TokenType::Space as usize, begin: 15, end: 16, content: String::from(" ")});
    }

    #[test]
    fn new_empty_token() {
        assert_eq!(Token::empty(TokenType::Heading as usize),
            Token {id: TokenType::Heading as usize, begin: 0, end: 0, content: String::from("")});
    }
}