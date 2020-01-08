#[derive(Debug)]
#[derive(PartialEq)]
pub struct Position {
    pub index: usize,
    pub line: usize,
}

impl Position {
    pub fn new(index: usize, line: usize) -> Position {
        Position {
            index,
            line,
        }
    }

    pub fn update(&mut self, position: (usize, usize)) {
        self.index = position.0;
        self.line = position.1;
    }

    pub fn increment(&mut self) {
        self.index += 1;
    }

    pub fn newline(&mut self) {
        self.line += 1;
    }

    pub fn set_index(&mut self, index: usize) {
        self.index = index;
    }

    pub fn set_line(&mut self, line: usize) {
        self.line = line;
    }
}