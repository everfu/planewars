import json
import os
import sys
from pygame.locals import *


def _config_path():
    # 打包版把设置写到用户目录，避免写入安装目录失败
    if getattr(sys, 'frozen', False):
        d = os.path.join(os.path.expanduser('~'), '.planewar')
        os.makedirs(d, exist_ok=True)
        return os.path.join(d, 'settings.json')
    return 'settings.json'

CONFIG_FILE = _config_path()

DEFAULT_KEYS={
    'up':K_w,
    'down':K_s,
    'left':K_a,
    'right':K_d,
    'bomb':K_SPACE,
    'pause':K_ESCAPE,
}

DEFAULTS={
    'mouse_control':True,
    'keys':DEFAULT_KEYS,
}

def _deep_copy():
    return json.loads(json.dumps(DEFAULTS))

def load_settings():
    cfg=_deep_copy()
    try:
        with open(CONFIG_FILE,'r') as f:
            data=json.load(f)
        if isinstance(data.get('mouse_control'),bool):
            cfg['mouse_control']=data['mouse_control']
        if isinstance(data.get('keys'),dict):
            for action in cfg['keys']:
                v=data['keys'].get(action)
                if isinstance(v,int) and 0<=v<512:
                    cfg['keys'][action]=v
    except:
        pass
    return cfg

def save_settings(cfg):
    try:
        with open(CONFIG_FILE,'w') as f:
            json.dump(cfg,f,indent=2)
        return True
    except:
        return False

def find_key_conflict(cfg,action,key):
    for a,k in cfg['keys'].items():
        if a!=action and k==key:
            return a
    return None

def reset_defaults(cfg):
    cfg['mouse_control']=DEFAULTS['mouse_control']
    cfg['keys']=dict(DEFAULT_KEYS)
    return cfg
