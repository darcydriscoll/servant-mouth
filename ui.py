# gui (User interface)
# Classes used for the user interface.
# By snarlinger (@gmail.com)
# Released under an MIT license

import pygame, pygame.freetype, pygame.mixer
from os import path

import string_manip

#pygame.mixer.pre_init(16000, -16, 2, 1024)
#pygame.mixer.pre_init(22050, -16, 2, 1024)
pygame.init()
pygame.mixer.quit()
pygame.mixer.init(16000, -16, 2, 512)

class Button(pygame.sprite.Sprite):
    """gui Button"""
    
    # Attributes
    active = True
    hover = False
    pressed = False
    executed = False
    # Text
    font_size = 14
    font = pygame.freetype.SysFont(None,font_size)
    font.pad = True
    line_height = font.get_sized_ascender(font_size) + abs(font.get_sized_descender(font_size))
    text = ''
    
    def __init__(self, wh, dest, text, colours, group):
        """Initialisation method for Button."""
        pygame.sprite.Sprite.__init__(self)
        self.group = group
        self.group.add(self)
        # Creating surface
        self.image = pygame.Surface(wh)
        self.colours = {
            'active': colours[0],
            'inactive': colours[1],
            'hover': colours[2],
            'pressed': colours[3]
        }
        self.image.fill(self.colours['active'])
        self.text_sprites = pygame.sprite.Group()
        self.create_text_sprites(text,wh,dest)
        self.text_blit()
        # Creating rectangle
        self.rect = self.image.get_rect()
        self.rect.topleft = dest
    
    def text_blit(self):
        """Blits text from text_sprites to the Button surface"""
        self.text_sprites.draw(self.image)
    
    def create_text_sprites(self, text, wh, dest):
        """Creates the text sprites and groups them in text_sprites"""
        self.text = text
        wrap = string_manip.text_wrap(self.font,self.text,wh[0])
        # Centring text
        centre_x = wh[0] / 2
        top_offset = (wh[1] - self.line_height * len(wrap)) / 2
        for line, str in enumerate(wrap):
            # Create surface and rectangle
            rend = self.font.render(wrap[line])
            rend[1].centerx = centre_x
            rend[1].top = line * self.line_height + top_offset
            # Create sprite
            spr = pygame.sprite.Sprite()
            spr.image = rend[0].convert_alpha()
            spr.rect = rend[1]
            # Add sprite to group
            self.text_sprites.add(spr)
    
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
            # Placeholder
            colour = (255,255,255)
        elif self.active:
            if not self.hover and not self.pressed:
                colour = self.colours['active']
            elif self.pressed:
                colour = self.colours['pressed']
            else:
                colour = self.colours['hover']
        else:
            colour = self.colours['inactive']
        # Updating surface
        self.image.fill(colour)
        self.text_blit()

class GroupButton(pygame.sprite.Group):
    """Group of gui Buttons"""
    selected = None
    
class Item(pygame.sprite.Sprite):
    """Inventory item Sprite class"""
    origin = (0,0)
    
    def __init__(self, image, name, desc, type, inventory):
        """Initialisation method for Item"""
        pygame.sprite.Sprite.__init__(self)
        self.inventory = inventory
        self.inventory.add(self)
        # Image
        self.image_copy = pygame.transform.scale(image,(55,55)).convert()
        self.image = self.image_copy.copy()
        self.image_scaled = pygame.transform.scale(image,(25,25)).convert()
        self.rect = self.image.get_rect()
        # Info
        self.name = name
        self.desc = desc
        self.type = type
        
class Inventory(pygame.sprite.Group):
    """Group of Items"""
    item_selected = None
    
    def set_dests(self):
        """Set the destinations of all items in the inventory"""
        y = 0
        for i, item in enumerate(self):
            # broken?
            rem = i % 2
            item.origin = (rem * 75, y)  # topleft
            item.rect.topleft = item.origin
            y += rem * 60
            
    def update_selected(self, phrases, animating):
        if self.item_selected is not None:
            states = pygame.mouse.get_pressed()
            if states[0] or states[2]:
                self.item_selected.rect.center = pygame.mouse.get_pos()
            else:
                if not animating:
                    mouse_pos = pygame.mouse.get_pos()
                    for phrase in phrases:
                        for spr in phrase:
                            if spr.rect.collidepoint(mouse_pos):
                                # Item interacting with phrase
                                print(phrase)
                                return
                # Item dropped
                self.item_selected.rect.topleft = self.item_selected.origin
                self.item_selected.rect.size = (55,55)
                self.item_selected.image = self.item_selected.image_copy
                self.item_selected = None


class Character(pygame.sprite.Sprite):
    """Single character sprite"""
    
    def __init__(self, colour, char, font_size, origin, index, line, phrase_group, shake_offset, should_anim, visible):
        """Initialisation method for Character"""
        pygame.sprite.Sprite.__init__(self)
        # Attributes
        self.colour = colour
        self.char = char # String
        self.font = pygame.freetype.SysFont(None,font_size)
        self.font.pad = True
        self.phrase_group = phrase_group
        try:
            self.phrase_group.add(self)
        except AttributeError:
            pass
        self.origin = origin # Topleft
        self.index = index # Index in paragraph
        self.line = line
        self.shake_offset = abs(shake_offset)
        self.should_anim = should_anim
        self.visible = visible
        # Render
        self.render()

    def render(self):
        """Renders the surface and rectangle of the character"""
        rend = self.font.render(self.char,self.colour)
        rend[1].top = self.origin[0]
        rend[1].left = self.origin[1]
        if self.shake_offset > 0:
            # Shaking effect
            pass # offset left and top by random number within pos and neg of given offset?
        self.image = rend[0].convert_alpha()
        self.rect = rend[1]
    
    def update(self, screen):
        """Blits the character to the screen"""
        screen.blit(self.image,self.rect)
        # add effects here

class GroupCharacters(pygame.sprite.Group):
    """Group of all Characters on screen"""
    animating = True
    phrase_hovered = None
    phrase_selected = None
    highlights = []
    i = 0
    # Sound
    sound = pygame.mixer.Sound(path.join('sound','sfx','text-blip3.ogg'))
    sound.set_volume(0.25)
    should_sound = False
    skip = True
    punctuation_pause = True
    
    def __init__(self, screen, phrases, base_speed):
        """Initialisation function for GroupCharacters"""
        pygame.sprite.Group.__init__(self)
        self.screen = screen
        self.phrases = phrases
        self.base_speed = base_speed
        self.speed = base_speed
    
    def play_sound(self):
        self.sound.play()
    
    def blit_highlights(self):
        """Blits each highlight in self.highlights"""
        for h in self.highlights:
            self.screen.blit(h[0],h[1])
    
    def draw_highlight(self, top_left, bottom_right, colour):
        """Returns the surface and rectangle for a given highlight"""
        surf = pygame.Surface((bottom_right[0] - top_left[0],bottom_right[1] - top_left[1]))
        surf.fill(colour)
        return (surf, surf.get_rect(topleft=top_left))
    
    def is_phrase_collision(phrase, mouse_coords):
        for ch in phrase:
            top_left = ch.rect.topleft
            bottom_right = ch.rect.bottomright
            if mouse_coords[0] >= top_left[0] and mouse_coords[0] <= bottom_right[0] and \
               mouse_coords[1] >= top_left[1] and mouse_coords[1] <= bottom_right[1]:
                return True
        else:
            return False
    
    def update(self, millis):
        """Blits the text to the screen"""
        chars = self.sprites()
        current_millis = pygame.time.get_ticks()
        # More characters to animate
        if self.i < len(self):
            # Enough time passed to animate?
            diff = current_millis - millis
            if diff >= self.speed:
                # If this is the start of a word, we want to ensure blit sound
                if not chars[self.i].should_anim:
                    self.skip = True
                # Deciding how many characters we need to blit
                overlap = int(diff / self.speed)
                for x in range(overlap):
                    try:
                        while not chars[self.i].should_anim:
                            self.i += 1
                        chars[self.i].update(self.screen)
                        self.i += 1
                        self.speed = self.base_speed
                        # Punctuation
                        if self.punctuation_pause and chars[self.i - 1].char in [',','.',':',';','?','!','-']:
                            print('punctuation')
                            self.speed += 150
                            break
                    except IndexError:
                        break
                millis = current_millis
                # Sound
                self.should_sound = True
                self.skip = not self.skip
        # No more characters to animate - Phrase selection
        else:
            millis = current_millis
            self.animating = False
            # Hover
            coord = pygame.mouse.get_pos()
            for phrase in self.phrases:
                for ch in phrase:
                    top_left = ch.rect.topleft
                    bottom_right = ch.rect.bottomright
                    # Is the cursor on a character of this phrase?
                    if coord[0] >= top_left[0] and coord[0] <= bottom_right[0] and \
                       coord[1] >= top_left[1] and coord[1] <= bottom_right[1]:
                        self.phrase_hovered = phrase
                        if self.phrase_hovered.known:
                            self.highlights = []
                            s = phrase.sprites()
                            top_left = s[0].rect.topleft
                            bottom_right = s[0].rect.bottomright
                            start_line = s[0].line
                            for x in s[1:]:
                                if x.line > start_line:
                                    # Appending highlight
                                    self.highlights.append(self.draw_highlight(top_left,bottom_right,(0,0,255)))
                                    # Resetting vars
                                    start_line = x.line
                                    top_left = x.rect.topleft
                                bottom_right = x.rect.bottomright
                            # Append final highlight and blit
                            self.highlights.append(self.draw_highlight(top_left,bottom_right,(0,0,255)))
                            self.blit_highlights()
                        # only one phrase selected at a time
                        break
                else:
                    continue
                # For loop for sprites was broken, so we break here too
                break
            else:
                self.phrase_hovered = None
            # Select
            mouse_states = pygame.mouse.get_pressed()
            if self.phrase_selected is not None and \
               not mouse_states[0] and not mouse_states[2]:
                if self.phrase_selected is self.phrase_hovered:
                    # Activate button
                    print('activation')
                    self.phrase_selected.known = True
                else:
                    # Deactivate button
                    self.phrase_selected = None
        # prev. characters
        for ch in chars[:self.i]:
            ch.update(self.screen)
        return millis
        
class Phrase(pygame.sprite.Group):
    """Group of Characters attached to this Phrase"""
    known = False
    
    def __init__(self, bounds):
        """Initialisation method for Phrase"""
        pygame.sprite.Group.__init__(self)
        self.bounds = bounds # tuple of indices

class Phrases(pygame.sprite.Group):
    """Group of all characters attached to a Phrase"""