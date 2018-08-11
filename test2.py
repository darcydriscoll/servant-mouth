# Test 2
# Prototyping core game features.
# By snarlinger (@gmail.com)
# Released under an MIT license

import sys, pygame, pygame.freetype, pygame.mixer
import xml.etree.ElementTree as ET
from pygame.locals import *
from os import path

import string_manip
import ui

pygame.init()

def tick(clock, fps):
    clock.tick(fps)
    pygame.display.flip()

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
    # Finding text
    tree = ET.parse(path.join('dialogue','test2.xml'))
    root = tree.getroot()
    
    char_groups = []
    paragraphs = root.findall('para')
    for paragraph in paragraphs:
        p_iter = paragraph.iter()
        p_iter.__next__() # skipping 'para'
        # Finding phrases and text
        phrases = []
        xml_i = 0
        text = ''
        phrase_start = None
        for el in p_iter:
            tag = el.tag
            print("Tag: " + tag)
            # tag cases
            if tag == 'phrasestart':
                phrase_start = xml_i
            elif tag == 'phraseend':
                assert phrase_start is not None
                phrases.append(ui.Phrase((phrase_start,xml_i - 1)))
                phrase_start = None
            elif tag == 'content':
                el_text = el.text
                xml_i += len(el_text)
                text += el_text
            else:
                raise ValueError('Unsupported tag');
        # Creating characters
        left_offset = x1 + 5
        top_offset = 5
        max_width = x2 - left_offset
        wrap = string_manip.text_wrap(f,text,max_width)
        text_height = f.get_rect(text).height
        char_group = ui.GroupCharacters(screen,phrases,30)
        char_groups.append(char_group);
        char_i = 0
        for line, str in enumerate(wrap):
            count_width = 0
            top = line * line_height + top_offset
            for ch in str:
                left = count_width + left_offset
                # Character indexed in phrase?
                for phrase in phrases:
                    bounds = phrase.bounds
                    if char_i >= bounds[0] and char_i <= bounds[1]:
                        phrase_group = phrase
                        break # No overlapping phrases
                else:
                    phrase_group = None
                # Animating spaces doesn't feel right, so we don't
                if ch == ' ': should_anim = False
                else: should_anim = True
                character = ui.Character((0,255,0),ch,f_size,(top,left),char_i,line,phrase_group,0,should_anim,True)
                count_width += character.rect.width
                char_group.add(character)
                char_i += 1
            char_i += 1
    char_group = char_groups[0]
    # Main loop
    millis = pygame.time.get_ticks()
    # inventory
    inventory = ui.Inventory()
    img = pygame.image.load(path.join('img','ding.png'))
    img2 = pygame.image.load(path.join('img','dingdong.jpg'))
    ui.Item(img,'placeholder','description','type',inventory)
    ui.Item(img2,'placeholder2','description2','type2',inventory)
    inventory.set_dests()
    # buttons
    button_group = ui.GroupButton()
    test_button = ui.Button((100,130),(200,200),'button man is here guys everyone crowd around',((255,0,0),(0,255,0),(0,0,255),(0,150,150)),button_group)
    test_button2 = ui.Button((50,30),(400,250),'button',((255,0,0),(0,255,0),(0,0,255),(0,150,150)),button_group)
    while True:
        if not char_group.animating:
            char_group = char_groups[1]
        
        # Event handling
        for e in pygame.event.get():
            # QUIT
            if e.type == pygame.QUIT: sys.exit()
            # Left click or right click
            if e.type == pygame.MOUSEBUTTONDOWN and (e.button == 1 or e.button == 3):
                # Inventory check
                for i, item in enumerate(inventory):
                    if item.rect.collidepoint(e.pos[0],e.pos[1]):
                        # Scale down
                        item.image = item.image_scaled
                        item.rect.size = (25,25)
                        # Make this item render first?
                        inventory.item_selected = item
                        break
                else:
                    # button
                    for button in button_group:
                        if button.rect.collidepoint(e.pos[0],e.pos[1]):
                            button_group.selected = button
                            break
                    # phrase selection
                    else:
                        if char_group.phrase_hovered is not None:
                            char_group.phrase_selected = char_group.phrase_hovered
        # inventory selection
        inventory.update_selected(phrases, char_group.animating)
        # Updating
        screen.fill(bg)
        # blit window
        pygame.draw.lines(screen,False,(0,0,0),pointlist,5)
        # blit text
        millis = char_group.update(millis)
        # blit buttons
        mouse_states = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        button_group.update(mouse_states, mouse_pos)
        for button in button_group:
            screen.blit(button.image,button.rect)
        # blit inventory
        for item in inventory:
            screen.blit(item.image,item.rect)
        
        tick(clock,fps)
        
        # Character sound
        if char_group.should_sound and not char_group.skip:
            char_group.sound.stop()
            char_group.play_sound()
            char_group.should_sound = False
        
if __name__ == "__main__":
    main()