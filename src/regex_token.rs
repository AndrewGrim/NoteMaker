use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use pyo3::PyObjectProtocol;

use crate::token_type::TokenType;

#[pyclass]
#[derive(Debug, PartialEq)]
pub struct RegexToken {
    pub id: usize,
    pub begin: usize,
    pub end: usize,
}

#[pymethods]
impl RegexToken {
    #[getter]
    fn get_id(&self) -> PyResult<u32> {
        Ok(self.id as u32)
    }

    #[getter]
    fn get_begin(&self) -> PyResult<u32> {
        Ok(self.begin as u32)
    }

    #[getter]
    fn get_end(&self) -> PyResult<u32> {
        Ok(self.end as u32)
    }
}

#[pyproto]
impl PyObjectProtocol for RegexToken {
    fn __str__(&self) -> PyResult<String> {
        Ok(format!(
            "RegexToken {{\n\tid: {}\n\tbegin: {}\n\tend: {}\n}}",
            self.id, self.begin, self.end
        ))
    }

    fn __repr__(&self) -> PyResult<String> {
        Ok(format!(
            "RegexToken {{\n\tid: {}\n\tbegin: {}\n\tend: {}\n}}",
            self.id, self.begin, self.end
        ))
    }
}

impl RegexToken {
    pub fn new(id: usize, begin: usize, end: usize) -> RegexToken {
        RegexToken { id, begin, end }
    }

    pub fn new_single(id: usize, begin: usize) -> RegexToken {
        RegexToken {
            id,
            begin,
            end: begin + 1,
        }
    }
}
