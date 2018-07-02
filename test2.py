import sys, pygame, pygame.freetype
from pygame.locals import *
from os import path

pygame.init()

class Button(pygame.sprite.Sprite):
    """UI Button"""
    # Attributes
    active = True
    hover = False
    pressed = False
    executed = False
    #         (active, inactive, hover, pressed)
    colours = ((0,0,0),(0,0,0),(0,0,0),(0,0,0))
    group = None
    # Text
    font_size = 14
    font = pygame.freetype.SysFont(None,font_size)
    font.pad = True
    line_height = font.get_sized_ascender(font_size) + abs(font.get_sized_descender(font_size))
    text = ''
    text_sprites = None # Group
    
    def __init__(self, wh, dest, text, colours, group):
        """Initialisation method for Button."""
        pygame.sprite.Sprite.__init__(self)
        group.add(self)
        self.group = group
        # Creating surface
        self.image = pygame.Surface(wh)
        self.colours = colours
        self.image.fill(colours[0])
        self.text_sprites = pygame.sprite.Group()
        self.create_text_sprites(text,wh,dest)
        self.text_blit()
        # Creating rectangle
        self.rect = self.image.get_rect()
        self.rect.topleft = dest
    
    def text_blit(self):
        """Blits text from text_sprites to the Button surface"""
        for spr in self.text_sprites:
            self.image.blit(spr.image,spr.rect)
    
    def create_text_sprites(self, text, wh, dest):
        """Create the text sprites and groups them in text_sprites"""
        self.text = text
        max_width = wh[0]
        wrap = text_wrap(self.font,self.text,max_width)
        line = 0
        while True:
            # Create surface and rectangle
            rend = self.font.render(wrap[0])
            rend[1].centerx = max_width / 2
            rend[1].top = line * self.line_height
            # Create sprite
            spr = pygame.sprite.Sprite()
            spr.image = rend[0].convert_alpha()
            spr.rect = rend[1]
            # Add sprite to group
            self.text_sprites.add(spr)
            # Next iteration?
            tail = wrap[1]
            if tail == '': break
            wrap = text_wrap(self.font,tail,max_width)
            line += 1
        y_offset = (wh[1] - self.line_height * (line + 1)) / 2
        for spr in self.text_sprites:
            spr.rect.top += y_offset
    
    def update_states(self, mouse_states, mouse_pos):
        """Updates the current state of the Button."""
        if self.rect.collidepoint(mouse_pos):
            self.hover = True
            if self.group.selected is self:
                if mouse_states[0] or mouse_states[2]:
                    self.pressed = True
                else:
                    # if executing this button
                    if self.pressed:
                        self.executed = True
                    self.pressed = False
        else:
            self.hover = False
            self.pressed = False
            if self.group.selected is self:
                if not mouse_states[0] and not mouse_states[2]:
                    self.group.selected = None
        
    def update(self, mouse_states, mouse_pos):
        """General update function for Button."""
        self.update_states(mouse_states, mouse_pos)
        colour = None
        if self.executed:
            colour = (255,255,255)
        elif self.active:
            if not self.hover and not self.pressed:
                colour = self.colours[0]
            elif self.pressed:
                colour = self.colours[3]
            else:
                colour = self.colours[2]
        else:
            colour = self.colours[1]
        # Updating surface
        self.image.fill(colour)
        self.text_blit()

class GroupButton(pygame.sprite.Group):
    """Group of UI Buttons"""
    # Attributes
    selected = None

def tick(clock, fps):
    clock.tick(fps)
    pygame.display.flip()

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
        if font.get_rect(word).width >= total_width:
            raise ValueError("Word too large", words, words[i])
        if i > 0:
            current_width += space
            concat += ' '
        current_width += font.get_rect(word).width
        if current_width > total_width:
            return concat[:-1], (concatenate(words[i:]))
        concat += word
    return concat, ''

def blit_text(line, lines, i, screen, phrase, millis, speed):
    # COULD PROBABLY CHANGE THIS SO IT COPIES RECTANGLE INSTEAD OF CREATING NEW ONE???
    current_millis = pygame.time.get_ticks()
    # If line applicable - current line
    if line < len(lines):
        # prev. characters
        for ch in lines[line][:i-1]:
            screen.blit(ch[0].image,ch[0].rect)
        if (current_millis - millis) >= speed:
            while not lines[line][i-1][1]:
                i += 1
            ch = lines[line][i-1]
            screen.blit(ch[0].image,ch[0].rect)
            i += 1
            if i > len(lines[line]):
                i = 1
                line += 1
            millis = current_millis
    # All lines animated - phrase selection
    else:
        # Phrase selection
        coord = pygame.mouse.get_pos()
        for spr in phrase:
            rect = spr.rect
            top_left = rect.topleft
            bottom_right = rect.bottomright
            if coord[0] >= top_left[0] and coord[0] <= bottom_right[0]:
                if coord[1] >= top_left[1] and coord[1] <= bottom_right[1]:
                    for spr in phrase:
                        rect = spr.rect
                        top_left = rect.topleft
                        bottom_right = rect.bottomright
                        highlight = pygame.Surface((bottom_right[0] - top_left[0],bottom_right[1] - top_left[1]))
                        highlight.fill((0,0,255))
                        screen.blit(highlight,highlight.get_rect(topleft=top_left))
                    break
    # prev. lines
    for l in lines[:line]:
        for ch in l:
            screen.blit(ch[0].image,ch[0].rect)
    return line, lines, i, screen, millis

def mouse_functions(inventory, select, phrases):
    states = pygame.mouse.get_pressed()
    if select is not None:
        if states[0] or states[2]:
            select[0][1].center = pygame.mouse.get_pos()
        else:
            mouse_pos = pygame.mouse.get_pos()
            for spr in phrases:
                if spr.rect.collidepoint(mouse_pos):
                    print("hella")
                    break
            else:
                select[0][1].topleft = select[1]
                select[0][1].size = (55,55)
                # selected item was recently appended to end of inventory list
                inventory[-1] = ((select[2],select[0][1]),select[1],select[2])
                select = None
    return select
        
def main():
    """Main game function."""
    clock = pygame.time.Clock()
    fps = 60
    dimensions = (640,480)
    screen = pygame.display.set_mode(dimensions)
    bg = (128,128,128)
    if not pygame.freetype.was_init(): sys.exit()
    f_size = 14
    f = pygame.freetype.SysFont(None,f_size)
    f.pad = True
    line_height = f.get_sized_ascender(f_size) + abs(f.get_sized_descender(f_size)) # can probably make this more efficient by using one of the other functions (size()?)
    # Making window (surf,rect)
    x_offset = 25
    y_offset = 1
    w = dimensions[0]; h = dimensions[1]
    x1 = w / 4 - x_offset; x2 = w / 2 + w / 4 - x_offset
    y1 = y_offset; y2 = h - y_offset
    pointlist = [(x1,y1),(x2,y1),(x2,y2),(x1,y2)]
    # Wrapping text
    test = 'hello how are you today i hope you are well'
    test_phrase = (18,29)
    phrase = pygame.sprite.Group()
    lines = []
    left_offset = 5
    left = x1 + left_offset
    top_offset = 5
    max_width = x2 - x1 - left_offset
    text = text_wrap(f,test,max_width)
    text_height = f.get_rect(test).height
    line = 0
    i = 0
    while True:
        chs = []
        count_width = 0
        for ch in text[0]:
            if ch == ' ': anim = False
            else: anim = True
            rend = f.render(ch,fgcolor=(0,255,0))
            rend = (rend[0].convert_alpha(),rend[1])
            rend[1].top = line * line_height + top_offset
            rend[1].left = count_width + left
            spr = pygame.sprite.Sprite()
            spr.image = rend[0]
            spr.rect = rend[1]
            if i >= test_phrase[0] and i <= test_phrase[1]:
                phrase.add(spr)
            chs.append((spr,anim))
            count_width += rend[1].width
            i += 1
        lines.append(chs)
        tail = text[1]
        if tail == '': break
        text = text_wrap(f,tail,max_width)
        line += 1
    # Main loop
    i = 1
    line = 0
    millis = pygame.time.get_ticks()
    img = pygame.image.load(path.join('img','ding.png'))
    img = pygame.transform.scale(img,(55,55)).convert()
    imgR = img.get_rect()
    imgR.topleft = (0,0)
    img2 = pygame.image.load(path.join('img','dingdong.jpg'))
    img2 = pygame.transform.scale(img2,(55,55)).convert()
    imgR2 = img2.get_rect()
    imgR2.topleft = (0,75)
    inv = [((img,imgR),(0,0),img.copy()),((img2,imgR2),(0,75),img2.copy())]
    selected_item = None
    button_group = GroupButton()
    test_button = Button((100,130),(200,200),'button man is here',((255,0,0),(0,255,0),(0,0,255),(0,150,150)),button_group)
    test_button2 = Button((50,30),(400,250),'button',((255,0,0),(0,255,0),(0,0,255),(0,150,150)),button_group)
    while True:
        # Event handling
        for e in pygame.event.get():
            # QUIT
            if e.type == pygame.QUIT: sys.exit()
            # Left click or right click
            if e.type == pygame.MOUSEBUTTONDOWN and (e.button == 1 or e.button == 3):
                # Inventory check
                for x in range(len(inv)):
                    if inv[x][0][1].collidepoint(e.pos[0],e.pos[1]):
                        # Scale down
                        new_img = pygame.transform.scale(inv[x][0][0],(25,25))
                        inv[x][0][1].size = (25,25)
                        new_item = ((new_img,inv[x][0][1]),inv[x][1],inv[x][2])
                        # Put scaled-down version to back of list (blits in front)
                        inv.append(new_item)
                        selected_item = new_item
                        del inv[x]
                        break
                else:
                    for button in button_group:
                        if button.rect.collidepoint(e.pos[0],e.pos[1]):
                            button_group.selected = button
                            break
        # mouse states
        selected_item = mouse_functions(inv,selected_item,phrase)
        # Updating
        screen.fill(bg)
        # blit window
        pygame.draw.lines(screen,False,(0,0,0),pointlist,5)
        # blit text
        speed = 25
        line, lines, i, screen, millis = blit_text(line,lines,i,screen,phrase,millis,speed)
        # blit inventory
        for item in inv:
            screen.blit(item[0][0],item[0][1])
        # blit buttons
        mouse_states = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        button_group.update(mouse_states, mouse_pos)
        for button in button_group:
            screen.blit(button.image,button.rect)
        tick(clock,fps)
        
if __name__ == "__main__":
    main()