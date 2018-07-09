# UI (User interface)
# Classes used for the user interface.
# By snarlinger (@gmail.com)
# Released under an MIT license

import pygame, pygame.freetype

import string_manip

pygame.init()

class Button(pygame.sprite.Sprite):
    """UI Button"""
    
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
    """Group of UI Buttons"""
    selected = None
    
class Item(pygame.sprite.Sprite):
    """Inventory item Sprite class"""
    
    def __init__(self, image, desc, type, inventory):
        """Initialisation method for Item"""
        pygame.sprite.Sprite.__init__(self)
        inventory.add(self)
        # Image
        self.image_copy = pygame.transform.scale(image,(55,55)).convert()
        self.image = self.image_copy.copy()
        self.image_scaled = pygame.transform.scale(image,(25,25)).convert()
        self.rect = self.image.get_rect()
        # Info
        self.desc = desc
        self.type = type
        
class Inventory(pygame.sprite.Group):
    """Group of Items"""
    
    def set_dests(self):
        """Set the destinations of all items in the inventory"""
        y = -60
        for i, item in enumerate(self):
            rem = i % 2
            item.rect.left = rem * 75
            item.rect.top = y
            y += rem * 60

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
        if self.phrase_group is not None:
            self.phrase_group.add(self)
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
    phrase_hovered = None
    phrase_selected = None
    highlights = []
    i = 0
    
    def __init__(self, screen, phrases, speed):
        """Initialisation function for GroupCharacters"""
        pygame.sprite.Group.__init__(self)
        self.screen = screen
        self.phrases = phrases
        self.speed = speed
    
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
            if (current_millis - millis) >= self.speed:
                while not chars[self.i].should_anim:
                    self.i += 1
                chars[self.i].update(self.screen)
                self.i += 1
                millis = current_millis
        # No more characters to animate - Phrase selection
        else:
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