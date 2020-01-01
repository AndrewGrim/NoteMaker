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
