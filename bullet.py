import pygame
from random import *

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self,bg_size,position,speed):
        pygame.sprite.Sprite.__init__(self)

        self.image=pygame.image.load('images/bullet1.png').convert_alpha()
        self.rect=self.image.get_rect()
        self.rect.centerx,self.rect.top=position
        self.speed=speed
        self.height=bg_size[1]
        self.active=False
        self.mask=pygame.mask.from_surface(self.image)

    def move(self):
        self.rect.top +=self.speed

        if self.rect.top>self.height:
            self.active=False

    def reset(self,position):
        self.rect.centerx,self.rect.top=position
        self.active=True

class Bullet1(pygame.sprite.Sprite):
    def __init__(self,position):
        pygame.sprite.Sprite.__init__(self)

        self.image=pygame.image.load('images/bullet1.png').convert_alpha()
        self.rect=self.image.get_rect()
        self.rect.left,self.rect.top=position
        self.speed=12
        self.active=False
        self.mask=pygame.mask.from_surface(self.image)


    def move(self):
        self.rect.top -=self.speed

        if self.rect.top<0:
            self.active=False

    def reset(self,position):
        self.rect.left,self.rect.top=position
        self.active=True

class Bullet2(pygame.sprite.Sprite):
    def __init__(self,position):
        pygame.sprite.Sprite.__init__(self)

        self.image=pygame.image.load('images/bullet2.png').convert_alpha()
        self.rect=self.image.get_rect()
        self.rect.left,self.rect.top=position
        self.speed=14
        self.active=False
        self.mask=pygame.mask.from_surface(self.image)


    def move(self):
        self.rect.top -=self.speed

        if self.rect.top<0:
            self.active=False

    def reset(self,position):
        self.rect.left,self.rect.top=position
        self.active=True
    
        
