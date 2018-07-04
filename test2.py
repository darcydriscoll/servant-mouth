# Test 2
# Prototyping core game features.
# By snarlinger (@gmail.com)
# Released under an MIT license

import sys, pygame, pygame.freetype
import xml.etree.ElementTree as ET
from pygame.locals import *
from os import path

import string_manip
import ui

pygame.init()

def tick(clock, fps):
    clock.tick(fps)
    pygame.display.flip()

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
    test_phrase = (6,10)
    # Wrapping text
    test = text
    phrase = pygame.sprite.Group()
    left_offset = x1 + 5
    top_offset = 5
    max_width = x2 - left_offset
    wrap = string_manip.text_wrap(f,test,max_width)
    print(wrap)
    text_height = f.get_rect(test).height
    char_group = ui.GroupCharacters(screen,phrase,10)
    i = 0
    for line, str in enumerate(wrap):
        count_width = 0
        top = line * line_height + top_offset
        for ch in str:
            left = count_width + left_offset
            if i >= test_phrase[0] and i <= test_phrase[1]:
                # Placeholder
                phrase_group = phrase
            else: phrase_group = None
            if ch == ' ': should_anim = False
            else: should_anim = True
            character = ui.Character((0,255,0),ch,f_size,(top,left),i,line,phrase_group,0,should_anim,True)
            count_width += character.rect.width
            char_group.add(character)
            i += 1
    # Main loop
    i = 0
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
        millis = char_group.update(millis)
        # blit buttons
        mouse_states = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        button_group.update(mouse_states, mouse_pos)
        for button in button_group:
            screen.blit(button.image,button.rect)
        # blit inventory
        for item in inv:
            screen.blit(item[0][0],item[0][1])
            
        tick(clock,fps)
        
if __name__ == "__main__":
    main()