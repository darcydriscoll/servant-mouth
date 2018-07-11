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
    tree = ET.parse(path.join('dialogue','test.xml'))
    root = tree.getroot()
    para = root.find('para')
    text = para.find('text').find('content').text
    # Setting phrases
    phrases = []
    for phrase in para.find('phrases'):
        attrib_start = phrase.attrib['start']
        attrib_end = phrase.attrib['end']
        try:
            start = int(attrib_start)
            end = int(attrib_end)
        except ValueError:
            print('ERROR: start or end value of phrase not an int. Skipping',attrib_start,attrib_end)
        else:
            phrases.append((attrib_start,attrib_end))
    phrases = [ui.Phrase((306,460)),ui.Phrase((21,30)),ui.Phrase((697,732)),ui.Phrase((0,37))]
    # Wrapping text
    test = text
    left_offset = x1 + 5
    top_offset = 5
    max_width = x2 - left_offset
    wrap = string_manip.text_wrap(f,test,max_width)
    text_height = f.get_rect(test).height
    char_group = ui.GroupCharacters(screen,phrases,500)
    i = 0
    for line, str in enumerate(wrap):
        count_width = 0
        top = line * line_height + top_offset
        for ch in str:
            left = count_width + left_offset
            # Character indexed in phrase?
            for phrase in phrases:
                bounds = phrase.bounds
                if i >= bounds[0] and i <= bounds[1]:
                    phrase_group = phrase
                    break # No overlapping phrases
            else:
                phrase_group = None
            # Animating spaces doesn't feel right, so we don't
            if ch == ' ': should_anim = False
            else: should_anim = True
            character = ui.Character((0,255,0),ch,f_size,(top,left),i,line,phrase_group,0,should_anim,True)
            count_width += character.rect.width
            char_group.add(character)
            i += 1
        i += 1
    # Main loop
    i = 0
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
        
if __name__ == "__main__":
    main()