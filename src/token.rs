use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use pyo3::PyObjectProtocol;

use crate::token_type::TokenType;

#[pyclass]
#[derive(Debug)]
pub struct Token {
    pub id: usize,
    pub begin: usize,
    pub end: usize,
    pub content: String,
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

    pub fn new_space(begin: usize) -> Token {
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