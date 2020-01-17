#[derive(Debug, Copy)]
pub enum Style {
    Text,
    Heading,
    Hidden,
    Code,
    Symbol,
    Test,
    Strike,
    Bold,
    Underline,
    Italic,
    Image,
    Link,
    Html,
    HtmlAttribute,
    Format,
    CodeBlockKeyword,
    CodeBlockSymbol,
    CodeBlockText,
    CodeBlockString,
    CodeBlockComment,
    CodeBlockFunction,
    CodeBlockClass,
    CodeBlockType,
    CodeBlockFlow,
    CodeBlockDigit,
    Comment,
    LinkUnderlined,
    ImageUnderlined,
}

impl Clone for Style {
    fn clone(&self) -> Self {
        *self
    }
}
