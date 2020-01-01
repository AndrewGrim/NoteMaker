use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use pyo3::PyObjectProtocol;

#[pyclass]
#[derive(Debug)]
pub struct Token {
    id: usize,
    begin: usize,
    end: usize,
    content: String,
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
}

#[derive(Debug)]
pub enum TokenType {
    Heading,
    HeadingEnd,
    HeadingText,
    BlockquoteBegin,
    BlockquoteEnd,
    BlockquoteText,
    Bold,
    Italic,
    Underline,
    Strike,
    Blockquote,
    Code,
    UnorderedList,
    OrderedList,
    Checked,
    UnChecked,
    Image,
    Link,
    Html,
    Newline,
    Tab,
    Space,
    Text,
    Error,
    CodeBegin,
    CodeEnd,
    BoldBegin,
    BoldEnd,
    UnderlineBegin,
    UnderlineEnd,
    ItalicBegin,
    ItalicEnd,
    HorizontalRule,
    UnorderedListBegin,
    UnorderedListEnd,
    ListItemBegin,
    ListItemEnd,
    ListItemText,
    OrderedListBegin,
    OrderedListEnd,
    CheckText,
    CheckEnd,
    ImageAltBegin,
    ImageAltEnd,
    ImageAltText,
    ImagePathBegin,
    ImagePathEnd,
    ImagePathText,
    LinkAltBegin,
    LinkAltEnd,
    LinkAltText,
    LinkPathBegin,
    LinkPathEnd,
    LinkPathText,
    HtmlBegin,
    HtmlEnd,
    HtmlText,
    HtmlAttributeText,
    StrikeBegin,
    StrikeEnd,
    CodeBlockBegin,
    CodeBlockEnd,
    Format,
    CodeBlockKeyword,
    CodeBlockSymbol,
    CodeBlock,
    CodeBlockString,
    CodeBlockType,
    CodeBlockFlow,
    CodeBlockDigit,
    CodeBlockClass,
    CodeBlockFunction,
    FormatBlockBegin,
    FormatBlockEnd,
    FormatBlockText,
}
