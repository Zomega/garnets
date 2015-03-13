class AsciiSprite:
    def __init__(self, chars, fg='', bg=''):
        self.chars = chars
        self.fg = fg
        self.bg = bg
        
    @property
    def size(self):
        lines = self.chars.split('\n')
        height = len(lines)
        width = max([ len(line) for line in lines ])
        return (width, height)
        
    def get(self, x, y):
        def grab(s, default):
            lines = s.split('\n')
            if y >= len(lines):
                return default
            if x >= len(lines[y]):
                return default
            return lines[y][x]
        return grab(self.chars, ' '), grab(self.fg, None), grab(self.bg, None)
