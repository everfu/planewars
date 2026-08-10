import pygame
import sys
import os
import traceback
from pygame.locals import *
from random import *

import myplane
import enemy
import bullet
import supply
import config


# PyInstaller 打包后，资源（images/sound/font）随程序一起提取，
# 这里把工作目录切到资源目录，保证所有相对路径加载都能找到文件
if getattr(sys, 'frozen', False):
    BASE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    os.chdir(BASE_DIR)

def data_file(name):
    # 打包版的可写数据（最高分、设置）放到用户目录，避免写入安装目录失败
    if getattr(sys, 'frozen', False):
        d = os.path.join(os.path.expanduser('~'), '.planewar')
        os.makedirs(d, exist_ok=True)
        return os.path.join(d, name)
    return name


pygame.init()
pygame.mixer.init()

bg_size=width,height=480,700
screen=pygame.display.set_mode(bg_size)
pygame.display.set_caption('飞机大战')

background=pygame.image.load('images/background.png')


BLACK=(0,0,0)
GREEN=(0,255,0)
RED=(255,0,0)
WHITE=(255,255,255)


#载入游戏音乐
pygame.mixer.music.load("sound/game_music.ogg")
pygame.mixer.music.set_volume(0.2)
bullet_sound = pygame.mixer.Sound("sound/bullet.wav")
bullet_sound.set_volume(0.2)
bomb_sound = pygame.mixer.Sound("sound/use_bomb.wav")
bomb_sound.set_volume(0.2)
supply_sound = pygame.mixer.Sound("sound/supply.wav")
supply_sound.set_volume(0.2)
get_bomb_sound = pygame.mixer.Sound("sound/get_bomb.wav")
get_bomb_sound.set_volume(0.2)
get_bullet_sound = pygame.mixer.Sound("sound/get_bullet.wav")
get_bullet_sound.set_volume(0.2)
upgrade_sound = pygame.mixer.Sound("sound/upgrade.wav")
upgrade_sound.set_volume(0.2)
enemy3_fly_sound = pygame.mixer.Sound("sound/enemy3_flying.wav")
enemy3_fly_sound.set_volume(0.2)
enemy1_down_sound = pygame.mixer.Sound("sound/enemy1_down.wav")
enemy1_down_sound.set_volume(0.2)
enemy2_down_sound = pygame.mixer.Sound("sound/enemy2_down.wav")
enemy2_down_sound.set_volume(0.2)
enemy3_down_sound = pygame.mixer.Sound("sound/enemy3_down.wav")
enemy3_down_sound.set_volume(0.5)
me_down_sound = pygame.mixer.Sound("sound/me_down.wav")
me_down_sound.set_volume(0.2)
enemy_bullet_sound = pygame.mixer.Sound("sound/bullet.wav")
enemy_bullet_sound.set_volume(0.06)
button_sound = pygame.mixer.Sound("sound/button.wav")
button_sound.set_volume(0.3)

def add_small_enemies(group1,group2,num):
    for i in range(num):
        e1=enemy.SmallEnemy(bg_size)
        group1.add(e1)
        group2.add(e1)

def add_mid_enemies(group1,group2,num):
    for i in range(num):
        e1=enemy.MidEnemy(bg_size)
        group1.add(e1)
        group2.add(e1)

def add_big_enemies(group1,group2,num):
    for i in range(num):
        e1=enemy.BigEnemy(bg_size)
        group1.add(e1)
        group2.add(e1)

def inc_speed(target,inc):
    for each in target:
        each.speed += inc


#每30秒发放一个补给包
SUPPLY_TIME=USEREVENT

#超级子弹定时器
DOUBLE_BULLET_TIME=USEREVENT+1

#解除我方无敌定时器
INVINCIBLE_TIME=USEREVENT+2


def load_record():
    try:
        with open(data_file('record.txt'), 'r') as f:
            return int(f.read().strip())
    except:
        return 0

def save_record(score):
    try:
        with open(data_file('record.txt'), 'w') as f:
            f.write(str(score))
    except:
        pass

def cjk_metrics_ok(font, sample):
    try:
        ms=font.metrics(sample)
        #所有字符都有字形，且字形度量不全都相同（排除仅含 .notdef 占位框的字体）
        return ms is not None and all(m is not None for m in ms) and len(set(ms))>1
    except:
        return False

def find_cjk_font():
    candidates=[
        #项目打包的游戏字体（得意黑）
        'font/smiley.ttf',
        #macOS
        '/System/Library/Fonts/PingFang.ttc',
        '/System/Library/Fonts/Hiragino Sans GB.ttc',
        '/System/Library/Fonts/STHeiti Light.ttc',
        '/System/Library/Fonts/STHeiti Medium.ttc',
        '/System/Library/Fonts/Supplemental/Songti.ttc',
        '/System/Library/Fonts/Supplemental/Arial Unicode.ttf',
        '/Library/Fonts/Arial Unicode.ttf',
        #Windows
        'C:/Windows/Fonts/msyh.ttc',
        'C:/Windows/Fonts/msyh.ttf',
        'C:/Windows/Fonts/simhei.ttf',
        'C:/Windows/Fonts/simsun.ttc',
        #Linux
        '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
        '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
        '/usr/share/fonts/truetype/arphic/uming.ttc',
    ]
    sample='飞机大战开始游戏暂停新纪录最高分移动方向键生命耗尽再来一次按退出继续点击右上角按钮×'
    for p in candidates:
        if not os.path.exists(p):
            continue
        try:
            f=pygame.font.Font(p,16)
            if cjk_metrics_ok(f,sample):
                return p
        except:
            continue
    #兜底：字体目录下自带的 font.ttf（若确实支持中文）
    try:
        f=pygame.font.Font('font/font.ttf',16)
        if cjk_metrics_ok(f,sample):
            return 'font/font.ttf'
    except:
        pass
    return None

CJK_FONT=find_cjk_font()
TITLE_CJK=CJK_FONT is not None

def game_font(size):
    return pygame.font.Font(CJK_FONT or 'font/font.ttf', size)


def draw_text_shadow(surface,font,text,center,shadow_color=(10,20,40)):
    shadow=font.render(text,True,shadow_color)
    main=font.render(text,True,WHITE)
    r=main.get_rect()
    r.center=(center[0]+3,center[1]+3)
    surface.blit(shadow,r)
    r.center=center
    surface.blit(main,r)

def start_screen(best_score,cfg):
    title_font=game_font(72)
    text_font=game_font(28)
    info_font=game_font(20)

    if TITLE_CJK:
        title='飞机大战'
        intro='驾驶战机，击落敌机，保卫天空！'
        best_label='最高分 : %d'%best_score
        start_label='开始游戏'
        settings_label='设置'
        quit_hint='按 Esc 退出'
    else:
        title='PLANE WAR'
        intro='Fly your plane, shoot them all down!'
        best_label='Best : %d'%best_score
        start_label='START GAME'
        settings_label='SETTINGS'
        quit_hint='Press Esc to quit'

    start_rect=pygame.Rect(0,0,220,56)
    start_rect.center=(width//2-100,470)
    settings_rect=pygame.Rect(0,0,160,56)
    settings_rect.center=(width//2+110,470)

    start_hover=False
    settings_hover=False
    clock=pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type==QUIT:
                pygame.quit()
                sys.exit()
            elif event.type==KEYDOWN:
                if event.key==K_ESCAPE:
                    return None
            elif event.type==MOUSEMOTION:
                start_hover=start_rect.collidepoint(event.pos)
                settings_hover=settings_rect.collidepoint(event.pos)
            elif event.type==MOUSEBUTTONDOWN:
                if event.button==1:
                    if start_rect.collidepoint(event.pos):
                        button_sound.play()
                        return 'start'
                    if settings_rect.collidepoint(event.pos):
                        button_sound.play()
                        return 'settings'

        screen.blit(background,(0,0))

        #标题（带投影）
        draw_text_shadow(screen,title_font,title,(width//2,130))

        #一句介绍
        intro_surf=text_font.render(intro,True,(210,225,255))
        intro_rect=intro_surf.get_rect()
        intro_rect.center=(width//2,205)
        screen.blit(intro_surf,intro_rect)

        #最高分
        best_surf=text_font.render(best_label,True,WHITE)
        best_rect=best_surf.get_rect()
        best_rect.center=(width//2,255)
        screen.blit(best_surf,best_rect)

        #开始游戏按钮
        start_color=(40,100,180) if not start_hover else (90,160,240)
        pygame.draw.rect(screen,start_color,start_rect,border_radius=14)
        pygame.draw.rect(screen,WHITE,start_rect,2,border_radius=14)
        start_surf=text_font.render(start_label,True,WHITE)
        screen.blit(start_surf,start_surf.get_rect(center=start_rect.center))

        #设置按钮
        settings_color=(70,80,100) if not settings_hover else (120,135,160)
        pygame.draw.rect(screen,settings_color,settings_rect,border_radius=14)
        pygame.draw.rect(screen,(160,170,190),settings_rect,2,border_radius=14)
        settings_surf=text_font.render(settings_label,True,WHITE)
        screen.blit(settings_surf,settings_surf.get_rect(center=settings_rect.center))

        #退出提示
        hint_surf=info_font.render(quit_hint,True,(150,160,180))
        hint_rect=hint_surf.get_rect()
        hint_rect.center=(width//2,height-30)
        screen.blit(hint_surf,hint_rect)

        pygame.display.flip()
        clock.tick(60)


def settings_screen(cfg):
    title_font=game_font(48)
    row_font=game_font(24)
    key_font=game_font(24)
    btn_font=game_font(24)
    info_font=game_font(20)

    if TITLE_CJK:
        screen_title='设置'
        rows=[('up','上移'),('down','下移'),('left','左移'),('right','右移'),\
              ('bomb','炸弹'),('pause','暂停'),('mouse','鼠标操控')]
        waiting_text='按任意键...（Esc 取消）'
        conflict_text='按键冲突：%s'
        on_text='开'
        off_text='关'
        reset_label='恢复默认'
        back_label='返回'
        hint_text='点击键位后按任意键重新绑定'
    else:
        screen_title='SETTINGS'
        rows=[('up','Move Up'),('down','Move Down'),('left','Move Left'),('right','Move Right'),\
              ('bomb','Bomb'),('pause','Pause'),('mouse','Mouse Control')]
        waiting_text='Press any key... (Esc to cancel)'
        conflict_text='Conflict with: %s'
        on_text='ON'
        off_text='OFF'
        reset_label='RESET'
        back_label='BACK'
        hint_text='Click a key row, then press a key to rebind'

    row_height=44
    row_pitch=52
    row_start=140
    row_rects={}
    for i,(action,label) in enumerate(rows):
        y=row_start+i*row_pitch
        row_rects[action]=pygame.Rect(60,y,360,row_height)

    reset_rect=pygame.Rect(0,0,180,52)
    reset_rect.center=(150,580)
    back_rect=pygame.Rect(0,0,160,52)
    back_rect.center=(350,580)

    waiting=None
    notice=''
    notice_frames=0
    clock=pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type==QUIT:
                pygame.quit()
                sys.exit()
            elif event.type==KEYDOWN:
                if waiting:
                    if event.key==K_ESCAPE:
                        waiting=None
                    else:
                        conflict=config.find_key_conflict(cfg,waiting,event.key)
                        if conflict:
                            conflict_label=dict(rows).get(conflict,conflict)
                            notice=conflict_text%conflict_label
                            notice_frames=120
                        else:
                            cfg['keys'][waiting]=event.key
                            waiting=None
                elif event.key==K_ESCAPE:
                    config.save_settings(cfg)
                    return
            elif event.type==MOUSEBUTTONDOWN:
                if event.button==1:
                    if waiting and row_rects[waiting].collidepoint(event.pos):
                        waiting=None
                        continue
                    for action,rect in row_rects.items():
                        if rect.collidepoint(event.pos):
                            button_sound.play()
                            if action=='mouse':
                                cfg['mouse_control']=not cfg['mouse_control']
                            elif waiting==action:
                                waiting=None
                            else:
                                waiting=action
                            break
                    else:
                        if reset_rect.collidepoint(event.pos):
                            button_sound.play()
                            config.reset_defaults(cfg)
                        elif back_rect.collidepoint(event.pos):
                            button_sound.play()
                            config.save_settings(cfg)
                            return

        if notice_frames:
            notice_frames-=1
            if not notice_frames:
                notice=''

        screen.blit(background,(0,0))

        #标题
        draw_text_shadow(screen,title_font,screen_title,(width//2,70))

        #提示文字
        hint_surf=info_font.render(hint_text,True,(160,175,195))
        hint_rect=hint_surf.get_rect()
        hint_rect.center=(width//2,115)
        screen.blit(hint_surf,hint_rect)

        #键位行
        for action,label in rows:
            rect=row_rects[action]
            base_color=(35,48,72)
            border_color=(90,110,145)
            if waiting==action:
                base_color=(60,80,40)
                border_color=(230,200,80)
            pygame.draw.rect(screen,base_color,rect,border_radius=10)
            pygame.draw.rect(screen,border_color,rect,2,border_radius=10)

            label_surf=row_font.render(label,True,WHITE)
            screen.blit(label_surf,(rect.left+16,rect.centery-label_surf.get_height()//2))

            if waiting==action:
                val_text=waiting_text
                val_color=(240,220,120)
            elif action=='mouse':
                val_text=on_text if cfg['mouse_control'] else off_text
                val_color=(120,230,140) if cfg['mouse_control'] else (210,120,120)
            else:
                val_text=pygame.key.name(cfg['keys'][action])
                val_color=WHITE
            val_surf=key_font.render(val_text,True,val_color)
            screen.blit(val_surf,(rect.right-16-val_surf.get_width(),\
                                  rect.centery-val_surf.get_height()//2))

        #恢复默认 / 返回
        pygame.draw.rect(screen,(60,90,140),reset_rect,border_radius=12)
        pygame.draw.rect(screen,WHITE,reset_rect,2,border_radius=12)
        reset_surf=btn_font.render(reset_label,True,WHITE)
        screen.blit(reset_surf,reset_surf.get_rect(center=reset_rect.center))

        pygame.draw.rect(screen,(70,80,100),back_rect,border_radius=12)
        pygame.draw.rect(screen,WHITE,back_rect,2,border_radius=12)
        back_surf=btn_font.render(back_label,True,WHITE)
        screen.blit(back_surf,back_surf.get_rect(center=back_rect.center))

        #提示信息（冲突等）
        if notice:
            notice_surf=info_font.render(notice,True,(255,150,120))
            notice_rect=notice_surf.get_rect()
            notice_rect.center=(width//2,660)
            screen.blit(notice_surf,notice_rect)

        pygame.display.flip()
        clock.tick(60)


def game_main(cfg):
    pygame.mixer.music.play(-1)
    enemy3_fly_sound.stop()
    pygame.time.set_timer(SUPPLY_TIME,30*1000)
    pygame.time.set_timer(DOUBLE_BULLET_TIME,0)
    pygame.time.set_timer(INVINCIBLE_TIME,0)

    #生成我方飞机
    me=myplane.MyPlane(bg_size)

    enemies=pygame.sprite.Group()

    #生成敌方小型飞机
    small_enemies=pygame.sprite.Group()
    add_small_enemies(small_enemies,enemies,15)

    #生成敌方中型飞机
    mid_enemies=pygame.sprite.Group()
    add_mid_enemies(mid_enemies,enemies,4)

    #生成敌方大型飞机
    big_enemies=pygame.sprite.Group()
    add_big_enemies(big_enemies,enemies,4)

    #生成普通子弹
    bullet1=[]
    bullet1_index=0
    BULLET1_NUM=4
    for i in range(BULLET1_NUM):
        bullet1.append(bullet.Bullet1(me.rect.midtop))

    #生成超级子弹
    bullet2=[]
    bullet2_index=0
    BULLET2_NUM=8
    for i in range(BULLET2_NUM//2):
        bullet2.append(bullet.Bullet2((me.rect.centerx-33,me.rect.centery)))
        bullet2.append(bullet.Bullet2((me.rect.centerx+30,me.rect.centery)))

    #生成敌方子弹
    enemy_bullets=[]
    ENEMY_BULLET_NUM=12
    for i in range(ENEMY_BULLET_NUM):
        enemy_bullets.append(bullet.EnemyBullet(bg_size,(0,-100),8))
    enemy_bullet_index=0

    #本机毁灭图片索引
    me_destroy_index=0

    clock=pygame.time.Clock()

    #设置难度级别
    level=1

    #全屏炸弹
    bomb_image=pygame.image.load('images/bomb.png').convert_alpha()
    bomb_rect=bomb_image.get_rect()
    bomb_font=game_font(48)
    bomb_num=3
    bomb_flash=pygame.Surface(bg_size)
    bomb_flash.fill(WHITE)
    bomb_flash_time=0

    #补给
    bullet_supply=supply.Bullet_Supply(bg_size)
    bomb_supply=supply.Bomb_Supply(bg_size)

    #标志是否使用超级子弹
    is_double_bullet=False

    #生命数量
    life_image=pygame.image.load('images/life.png').convert_alpha()
    life_rect=life_image.get_rect()
    life_num=3

    #游戏结束界面
    gameover_font=game_font(48)
    again_image=pygame.image.load('images/again.png').convert_alpha()
    again_rect=again_image.get_rect()
    gameover_image=pygame.image.load('images/gameover.png').convert_alpha()
    gameover_rect=gameover_image.get_rect()

    #用于阻值重复打开文件
    recorded=False
    new_record=False

    #用于切换飞机移动图片
    switch_image=True

    #统计得分
    score=0
    score_font=game_font(36)

    #标志是否暂停游戏
    paused=False
    pause_nor_image=pygame.image.load('images/pause_nor.png').convert_alpha()
    pause_pressed_image=pygame.image.load('images/pause_pressed.png').convert_alpha()
    resume_nor_image=pygame.image.load('images/resume_nor.png').convert_alpha()
    resume_pressed_image=pygame.image.load('images/resume_pressed.png').convert_alpha()
    paused_rect=pause_nor_image.get_rect()
    paused_rect.right,paused_rect.top=width-10,10
    paused_image=pause_nor_image
    pause_font=game_font(36)
    pause_mask=pygame.Surface(bg_size)
    pause_mask.fill(BLACK)
    quit_rect=pygame.Rect(0,0,180,52)
    quit_rect.center=(width//2,height//2+95)
    quit_hover=False

    def set_paused(value):
        nonlocal paused,paused_image
        paused=value
        if paused:
            paused_image=resume_nor_image
            pygame.time.set_timer(SUPPLY_TIME,0)
            pygame.mixer.music.pause()
            pygame.mixer.pause()
        else:
            paused_image=pause_nor_image
            pygame.time.set_timer(SUPPLY_TIME,30*1000)
            pygame.mixer.music.unpause()
            pygame.mixer.unpause()

    def me_hurt():
        me.energy=0
        me.active=False

    running=True

    #用于延时
    delay=100

    while running:
        for event in pygame.event.get():
            if event.type==QUIT:
                pygame.quit()
                sys.exit()
            elif event.type==MOUSEBUTTONDOWN:
                if event.button==1 and paused_rect.collidepoint(event.pos):
                    set_paused(not paused)
                elif event.button==1 and paused and quit_rect.collidepoint(event.pos):
                    button_sound.play()
                    pygame.mixer.music.stop()
                    return 'quit'
            elif event.type==MOUSEMOTION:
                if paused_rect.collidepoint(event.pos):
                    if paused:
                        paused_image=resume_pressed_image
                    else:
                        paused_image=pause_pressed_image
                else:
                    if paused:
                        paused_image=resume_nor_image
                    else:
                        paused_image=pause_nor_image
                quit_hover=quit_rect.collidepoint(event.pos)
                #鼠标控制飞机移动
                if cfg['mouse_control'] and life_num and not paused and me.active:
                    me.rect.centerx=min(max(event.pos[0],me.rect.width//2),\
                                        width-me.rect.width//2)
                    me.rect.centery=min(max(event.pos[1],me.rect.height//2),\
                                        height-60-me.rect.height//2)
            elif event.type==KEYDOWN:
                if event.key==cfg['keys']['bomb']:
                    if not paused and life_num and bomb_num:
                        bomb_num-=1
                        bomb_sound.play()
                        bomb_flash_time=30
                        for each in enemies:
                            if each.rect.bottom>0:
                                each.active=False
                elif event.key==cfg['keys']['pause']:
                    if life_num:
                        set_paused(not paused)
                    else:
                        return 'quit'
            elif event.type==SUPPLY_TIME:
                supply_sound.play()
                if choice([True,False]):
                    bomb_supply.reset()
                else:
                    bullet_supply.reset()
            elif event.type==DOUBLE_BULLET_TIME:
                is_double_bullet=False
                pygame.time.set_timer(DOUBLE_BULLET_TIME,0)
            elif event.type==INVINCIBLE_TIME:
                me.invincible=False
                pygame.time.set_timer(INVINCIBLE_TIME,0)

        #根据用户的得分增加难度
        if level==1 and score>50000:
            level=2
            upgrade_sound.play()
            #增加3架小飞机，2架中敌机，1架大敌机
            add_small_enemies(small_enemies,enemies,3)
            add_mid_enemies(mid_enemies,enemies,2)
            add_big_enemies(big_enemies,enemies,1)

            #提升小飞机速度
            inc_speed(small_enemies,1)
        elif level==2 and score>300000:
            level=3
            upgrade_sound.play()
            #增加5架小飞机，3架中敌机，2架大敌机
            add_small_enemies(small_enemies,enemies,5)
            add_mid_enemies(mid_enemies,enemies,3)
            add_big_enemies(big_enemies,enemies,2)

            #提升小中飞机速度
            inc_speed(small_enemies,1)
            inc_speed(mid_enemies,1)
        elif level==3 and score>600000:
            level=4
            upgrade_sound.play()
            #增加5架小飞机，3架中敌机，2架大敌机
            add_small_enemies(small_enemies,enemies,5)
            add_mid_enemies(mid_enemies,enemies,3)
            add_big_enemies(big_enemies,enemies,2)

            #提升小中飞机速度
            inc_speed(small_enemies,1)
            inc_speed(mid_enemies,1)
        elif level==4 and score>1000000:
            level=5
            upgrade_sound.play()
            #增加5架小飞机，3架中敌机，2架大敌机
            add_small_enemies(small_enemies,enemies,5)
            add_mid_enemies(mid_enemies,enemies,3)
            add_big_enemies(big_enemies,enemies,2)

            #提升小中飞机速度
            inc_speed(small_enemies,1)
            inc_speed(mid_enemies,1)


        screen.blit(background,(0,0))

        if life_num and not paused:
            #检测用户键盘操作
            key_pressed=pygame.key.get_pressed()

            if key_pressed[cfg['keys']['up']]:
                me.moveUp()
            if key_pressed[cfg['keys']['down']]:
                me.moveDown()
            if key_pressed[cfg['keys']['left']]:
                me.moveLeft()
            if key_pressed[cfg['keys']['right']]:
                me.moveRight()

            #绘制全屏炸弹补给并检测是否获得
            if bomb_supply.active:
                bomb_supply.move()
                screen.blit(bomb_supply.image,bomb_supply.rect)
                if pygame.sprite.collide_mask(bomb_supply,me):
                    get_bomb_sound.play()
                    if bomb_num<3:
                        bomb_num+=1
                    bomb_supply.active=False

            #绘制超级子弹补给并检测是否获得
            if bullet_supply.active:
                bullet_supply.move()
                screen.blit(bullet_supply.image,bullet_supply.rect)
                if pygame.sprite.collide_mask(bullet_supply,me):
                    get_bullet_sound.play()
                    is_double_bullet=True
                    pygame.time.set_timer(DOUBLE_BULLET_TIME,18*1000)
                    bullet_supply.active=False

            #发射子弹
            if not(delay%10):
                bullet_sound.play()
                if is_double_bullet:
                    bullets=bullet2
                    bullets[bullet2_index].reset((me.rect.centerx-33,me.rect.centery))
                    bullets[bullet2_index+1].reset((me.rect.centerx+30,me.rect.centery))
                    bullet2_index=(bullet2_index+2)%BULLET2_NUM
                else:
                    bullets=bullet1
                    bullets[bullet1_index].reset(me.rect.midtop)
                    bullet1_index=(bullet1_index+1)%BULLET1_NUM

            #检测子弹是否击中敌机
            for b in bullets:
                if b.active:
                    b.move()
                    screen.blit(b.image,b.rect)
                    enemy_hit=pygame.sprite.spritecollide(b,enemies,False,pygame.sprite.collide_mask)
                    if enemy_hit:
                        b.active=False
                        for e in enemy_hit:
                            if e in mid_enemies or e in big_enemies:
                                e.hit=True
                                e.energy-=1
                                if e.energy==0:
                                    e.active=False
                            else:
                                e.active=False

            #敌机射击
            fire_speed=1+(level-1)//2
            for each in mid_enemies:
                if each.can_fire(fire_speed):
                    enemy_bullets[enemy_bullet_index].reset(\
                            (each.rect.centerx,each.rect.bottom))
                    enemy_bullet_index=(enemy_bullet_index+1)%ENEMY_BULLET_NUM
                    enemy_bullet_sound.play()
            for each in big_enemies:
                if each.can_fire(fire_speed):
                    enemy_bullets[enemy_bullet_index].reset(\
                            (each.rect.centerx,each.rect.bottom))
                    enemy_bullet_index=(enemy_bullet_index+1)%ENEMY_BULLET_NUM
                    enemy_bullets[enemy_bullet_index].reset(\
                            (each.rect.centerx-22,each.rect.bottom))
                    enemy_bullet_index=(enemy_bullet_index+1)%ENEMY_BULLET_NUM
                    enemy_bullets[enemy_bullet_index].reset(\
                            (each.rect.centerx+22,each.rect.bottom))
                    enemy_bullet_index=(enemy_bullet_index+1)%ENEMY_BULLET_NUM
                    enemy_bullet_sound.play()

            #敌方子弹移动与检测
            for b in enemy_bullets:
                if b.active:
                    b.move()
                    screen.blit(b.image,b.rect)
                    if me.active and not me.invincible and \
                       pygame.sprite.collide_mask(b,me):
                        b.active=False
                        me_hurt()

            #绘制大型敌机
            for each in big_enemies:
                if each.active:
                    each.move()
                    #大型机飞行音效（进入屏幕时播放一次）
                    if not each.sound_played and each.rect.top>=0:
                        each.sound_played=True
                        enemy3_fly_sound.play(-1)
                    if each.hit:
                        #绘制被打倒图片
                        screen.blit(each.image_hit,each.rect)
                        each.hit=False
                    else:
                        if switch_image:
                            screen.blit(each.image1,each.rect)
                        else:
                            screen.blit(each.image2,each.rect)
                    #绘制血槽
                    pygame.draw.line(screen,BLACK,\
                                     (each.rect.left,each.rect.top-5),\
                                     (each.rect.right,each.rect.top-5),\
                                     2)
                    #当生命大于%20显示绿色，否则显示红色
                    energy_remain=each.energy/enemy.BigEnemy.energy
                    if energy_remain>0.2:
                        energy_color=GREEN
                    else:
                        energy_color=RED

                    pygame.draw.line(screen,energy_color,\
                                     (each.rect.left,each.rect.top-5),\
                                     (each.rect.left+each.rect.width*energy_remain,\
                                      each.rect.top-5),2)
                else:
                    #大飞机毁灭
                    if not(delay%3):
                        if each.destroy_index==0:
                            enemy3_down_sound.play()
                        screen.blit(each.destroy_images[each.destroy_index],each.rect)
                        each.destroy_index=(each.destroy_index+1)%6
                        if each.destroy_index==0:
                            enemy3_fly_sound.stop()
                            score+=10000
                            each.reset()

            #绘制中型机
            for each in mid_enemies:
                if each.active:
                    each.move()

                    if each.hit:
                        screen.blit(each.image_hit,each.rect)
                        each.hit=False
                    else:
                        screen.blit(each.image,each.rect)
                    #绘制血槽
                    pygame.draw.line(screen,BLACK,\
                                     (each.rect.left,each.rect.top-5),\
                                     (each.rect.right,each.rect.top-5),\
                                     2)
                    #当生命大于%20显示绿色，否则显示红色
                    energy_remain=each.energy/enemy.MidEnemy.energy
                    if energy_remain>0.2:
                        energy_color=GREEN
                    else:
                        energy_color=RED

                    pygame.draw.line(screen,energy_color,\
                                     (each.rect.left,each.rect.top-5),\
                                     (each.rect.left+each.rect.width*energy_remain,\
                                      each.rect.top-5),2)
                else:
                    #中飞机毁灭
                    if not(delay%3):
                        if each.destroy_index==0:
                            enemy2_down_sound.play()
                        screen.blit(each.destroy_images[each.destroy_index],each.rect)
                        each.destroy_index=(each.destroy_index+1)%4
                        if each.destroy_index==0:
                            score+=6000
                            each.reset()

            #绘制小型机
            for each in small_enemies:
                if each.active:
                    each.move()
                    screen.blit(each.image,each.rect)
                else:
                    #小飞机毁灭
                    if not(delay%3):
                        if each.destroy_index==0:
                            enemy1_down_sound.play()
                        screen.blit(each.destroy_images[each.destroy_index],each.rect)
                        each.destroy_index=(each.destroy_index+1)%4
                        if each.destroy_index==0:
                            score+=1000
                            each.reset()

            #检测我方飞机是否被撞
            enemies_down=pygame.sprite.spritecollide(me,enemies,False,pygame.sprite.collide_mask)
            if enemies_down and not me.invincible:
                for each in enemies_down:
                    each.active=False
                me_hurt()

            #绘制我方飞机
            if me.active:
                if not me.invincible or not(delay%10)<5:
                    if switch_image:
                        screen.blit(me.image1,me.rect)
                    else:
                        screen.blit(me.image2,me.rect)
            else:
                #本机毁灭
                if not(delay%3):
                    if me_destroy_index==0:
                        me_down_sound.play()
                    screen.blit(me.destroy_images[me_destroy_index],me.rect)
                    me_destroy_index=(me_destroy_index+1)%4
                    if me_destroy_index==0:
                        life_num-=1
                        me.reset()
                        pygame.time.set_timer(INVINCIBLE_TIME,3*1000)

            #绘制全屏炸弹数量
            bomb_text=bomb_font.render('× %d'%bomb_num,True,WHITE)
            text_rect=bomb_text.get_rect()
            screen.blit(bomb_image,(10,height-10-bomb_rect.height))
            screen.blit(bomb_text,(20+bomb_rect.width,height-5-text_rect.height))

            #绘制剩余生命数量
            if life_num:
                for i in range(life_num):
                    screen.blit(life_image,\
                                (width-10-(i+1)*life_rect.width,\
                                 height-10-life_rect.height))
            #绘制得分
            score_text=score_font.render('Score : %s'%str(score),True,WHITE)
            screen.blit(score_text,(10,5))

            #绘制等级
            level_text=score_font.render('Level : %d'%level,True,WHITE)
            screen.blit(level_text,(10,54))

        #绘制游戏结束画面
        elif life_num==0:
            #背景音乐停止
            pygame.mixer.music.stop()

            #停止全部音效
            pygame.mixer.stop()
            enemy3_fly_sound.stop()

            #停止发放补给
            pygame.time.set_timer(SUPPLY_TIME,0)

            if not recorded:
                #读取历史最高分
                recorded=True
                record_score=load_record()

                #如果玩家得分高于历史最高得分，存档
                if score>record_score:
                    record_score=score
                    save_record(score)
                    new_record=True

            #绘制结束界面
            record_score_text=score_font.render("Best : %d"%record_score,True,WHITE)
            screen.blit(record_score_text,(50,50))

            if new_record:
                new_record_text=score_font.render(\
                        ('新纪录!' if TITLE_CJK else 'New Record!'),True,GREEN)
                screen.blit(new_record_text,(50,90))

            gameover_text1=gameover_font.render("Your Score",True,WHITE)
            gameover_text1_rect=gameover_text1.get_rect()
            gameover_text1_rect.left,gameover_text1_rect.top=\
                                 (width-gameover_text1_rect.width)//2,height//3
            screen.blit(gameover_text1,gameover_text1_rect)

            gameover_text2=gameover_font.render(str(score),True,WHITE)
            gameover_text2_rect=gameover_text2.get_rect()
            gameover_text2_rect.left,gameover_text2_rect.top=\
                                 (width-gameover_text2_rect.width)//2,\
                                 gameover_text1_rect.bottom+10
            screen.blit(gameover_text2,gameover_text2_rect)

            again_rect.left,again_rect.top=\
                             (width-again_rect.width)//2,\
                             gameover_text2_rect.bottom+50
            screen.blit(again_image,again_rect)

            gameover_rect.left,gameover_rect.top=\
                                (width-again_rect.width)//2,\
                                again_rect.bottom+10
            screen.blit(gameover_image,gameover_rect)

            #检测用户的鼠标操作
            if pygame.mouse.get_pressed()[0]:
                pos=pygame.mouse.get_pos()
                #如果用户点击"再来一次"，重新开始游戏
                if again_rect.left<pos[0]<again_rect.right and \
                   again_rect.top<pos[1]<again_rect.bottom:
                    return 'again'
                #如果用户点击"结束游戏"，返回开始界面
                elif gameover_rect.left<pos[0]<gameover_rect.right and \
                     gameover_rect.top<pos[1]<gameover_rect.bottom:
                    return 'quit'

        else:
            #暂停画面
            pause_mask.set_alpha(120)
            screen.blit(pause_mask,(0,0))
            paused_text=pause_font.render(('已暂停' if TITLE_CJK else 'PAUSED'),\
                                          True,WHITE)
            paused_text_rect=paused_text.get_rect()
            paused_text_rect.center=(width//2,height//2-30)
            screen.blit(paused_text,paused_text_rect)
            resume_key=pygame.key.name(cfg['keys']['pause'])
            resume_hint=pause_font.render(\
                (('按 %s 继续'%resume_key) if TITLE_CJK else ('Press %s to resume'%resume_key)),\
                                          True,WHITE)
            resume_hint_rect=resume_hint.get_rect()
            resume_hint_rect.center=(width//2,height//2+30)
            screen.blit(resume_hint,resume_hint_rect)

            #退出按钮
            quit_color=(150,60,60) if not quit_hover else (200,90,90)
            pygame.draw.rect(screen,quit_color,quit_rect,border_radius=12)
            pygame.draw.rect(screen,WHITE,quit_rect,2,border_radius=12)
            quit_surf=pause_font.render(('退出游戏' if TITLE_CJK else 'QUIT'),\
                                        True,WHITE)
            screen.blit(quit_surf,quit_surf.get_rect(center=quit_rect.center))

        #绘制暂停按钮
        screen.blit(paused_image,paused_rect)

        #全屏炸弹特效
        if bomb_flash_time>0:
            bomb_flash_time-=1
            bomb_flash.set_alpha(int(140*bomb_flash_time/30))
            screen.blit(bomb_flash,(0,0))

        #切换图片
        if not(delay%5):
            switch_image=not switch_image
        delay-=1
        if not delay:
            delay=100
        pygame.display.flip()

        clock.tick(60)


def main():
    cfg=config.load_settings()
    while True:
        action=start_screen(load_record(),cfg)
        if action is None:
            return
        if action=='settings':
            settings_screen(cfg)
            continue
        while True:
            result=game_main(cfg)
            if result=='again':
                #游戏结束后点击"再来一次"，直接重新开始
                continue
            break
        #点击"结束游戏"，返回开始界面

if __name__=='__main__':
    try:
        main()
    except SystemExit:
        pass
    except:
        traceback.print_exc()
        pygame.quit()
        input("Press <enter>")
