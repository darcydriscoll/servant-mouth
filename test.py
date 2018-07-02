import sys, pygame, pygame.freetype
from pygame.locals import *

def text_wrap(font, text, total_width):
    """Returns the text that can fit in a given width and the text that can't."""
    def concatenate(lst):
        """Joins all strings in a given list into a string of words."""
        str = ''
        for x in lst:
            str += x + ' '
        return str[:-1]
    size = font.size
    words = text.split()
    space = font.get_rect(' ').width
    current_width = 0
    concat = ''
    for i in range(len(words)):
        word = words[i]
        if i > 0:
            current_width += space
            concat += ' '
        current_width += font.get_rect(word).width
        if current_width > total_width:
            return concat[:-1], (concatenate(words[i:]))
        concat += word
    return concat, ''
    
def main():
    """Main game function."""
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    if not pygame.freetype.was_init(): sys.exit()
    f = pygame.freetype.SysFont(None,50)
    f.pad = True
    line_height = f.get_sized_ascender(50) + abs(f.get_sized_descender(50))
    # Wrapping text
    test = 'hello world how are you today i hope you are well okay bye'
    lines = []
    text = text_wrap(f,test,640)
    text_height = f.get_rect(test).height
    while True:
        lines.append(text[0])
        tail = text[1]
        if tail == '': break
        else: text = text_wrap(f,tail,640)
    # Main loop
    ch = 1
    line = 0
    print(len(lines))
    while True:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
        # Updating
        screen.fill((128, 128, 128))
        # Prev. lines
        if line > 0:
            for i in range(len(lines[:line])):
                rend = f.render(lines[i])
                rend[1].top = i * line_height
                rend[1].left = 0
                screen.blit(rend[0],rend[1])
        # Current line
        if line < len(lines):
            while lines[line][ch-1] == ' ':
                ch += 1
            chs = f.render(lines[line][:ch])
            chs[1].top = line * line_height
            chs[1].left = 0
            chs[1].height = line_height
            screen.blit(chs[0],chs[1])
            ch += 1
            if ch >= len(lines[line]):
                ch = 0
                line += 1
        pygame.time.delay(250)
        pygame.display.flip()
        
if __name__ == "__main__":
    main()