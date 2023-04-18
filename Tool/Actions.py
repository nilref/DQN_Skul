# Define the actions we may need during training
# You can define your actions here

from Tool.SendKey import PressKey, ReleaseKey
from Tool.WindowsAPI import grab_screen
import time
import cv2
import threading

# Hash code for key we may use: https://docs.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes?redirectedfrom=MSDN
L_MOUSE_BTN = 0x01
R_MOUSE_BTN = 0x02

UP_ARROW = 0x26
DOWN_ARROW = 0x28
LEFT_ARROW = 0x25
RIGHT_ARROW = 0x27

L_SHIFT = 0xA0

ESC = 0x1B

F1=0x70
F2=0x71

A = 0x41
S = 0x53
D = 0x44
F = 0x46

Z = 0x5A
X = 0x58
C = 0x43

# move actions
# 0
def Nothing():
    ReleaseKey(LEFT_ARROW)
    ReleaseKey(RIGHT_ARROW)
    pass

# Move
# 0
def Move_Left():
    PressKey(LEFT_ARROW)
    time.sleep(0.01)
# 1
def Move_Right():
    PressKey(RIGHT_ARROW)
    time.sleep(0.01)

# 2
def Turn_Left():
    PressKey(LEFT_ARROW)
    time.sleep(0.01)
    ReleaseKey(LEFT_ARROW)

# 3
def Turn_Right():
    PressKey(RIGHT_ARROW)
    time.sleep(0.01)
    ReleaseKey(RIGHT_ARROW)

# 4
def Turn_Up():
    PressKey(UP_ARROW)
    time.sleep(0.01)
    ReleaseKey(UP_ARROW)

# 5
def Turn_Down():
    PressKey(DOWN_ARROW)
    time.sleep(0.01)
    ReleaseKey(DOWN_ARROW)

# ----------------------------------------------------------------------

# other actions
# 0
def Attack():
    PressKey(X)
    time.sleep(0.15)
    ReleaseKey(X)
    Nothing()
    time.sleep(0.01)
# 1
def Jump():
    PressKey(C)
    time.sleep(0.2) 
    ReleaseKey(C)
    Nothing()
# 2
def Rush():
    PressKey(Z)
    time.sleep(0.2)
    ReleaseKey(Z)
    Nothing()
# 3
def Skill_A():
    PressKey(A)
    time.sleep(0.2)
    ReleaseKey(A)
    Nothing()
    time.sleep(0.3)
# 4
def Skill_S():
    PressKey(S)
    time.sleep(0.2)
    ReleaseKey(S)
    Nothing()
    time.sleep(0.3)
# 5 
def Skill_D():
    PressKey(D)
    time.sleep(0.2)
    ReleaseKey(D)
    Nothing()
    time.sleep(0.3)
    
def Esc():
    PressKey(ESC)
    time.sleep(0.2)
    ReleaseKey(ESC)

# 打开开发者菜单
def OpenDevMenu():
    PressKey(F2)
    time.sleep(0.2)
    ReleaseKey(F2)
    
# F键
def Interact():
    PressKey(F)
    time.sleep(0.1)
    ReleaseKey(F)

def restart(self_hp, enemies_count):
    if(self_hp < 0):
        # 按X重开
        Attack()
    else:
        # 手动重开
        Esc()
        time.sleep(0.5)
        # 按下键一次
        Turn_Down()
        time.sleep(0.5)
        # 按C键重开
        Jump()
        time.sleep(0.5)
        # 按左键一次
        Turn_Left()
        time.sleep(0.5)
        Jump()
    Nothing()
    time.sleep(5)
    
def play():
    # 向右走下悬崖开始游戏
    Move_Right()
    time.sleep(13)
    Nothing()
    time.sleep(1)
    Interact()
    time.sleep(0.1)
    Move_Right()
    time.sleep(2)
    Nothing()
    time.sleep(1)
    Interact()

def Reload_Map():
    # 打开开发者菜单
    OpenDevMenu()
    time.sleep(0.1)
    # 向下一次
    Turn_Down()
    time.sleep(0.1)
    # 向右一次
    Turn_Right()
    time.sleep(0.1)
    # 按C键确认
    Jump()
    time.sleep(0.1)
    # 再次触发该函数，就是关闭开发者菜单
    OpenDevMenu()
    
# 将开发者菜单调节至地图选择页面
def Init_DevMenu_T0_MapSelect():
    OpenDevMenu()
    time.sleep(0.1)
    Jump()
    time.sleep(0.1)
    OpenDevMenu()

# List for action functions
Actions = [Attack, Jump, Rush, Skill_A, Skill_S]
Directions = [Move_Left, Move_Right, Turn_Left, Turn_Right, Turn_Up, Turn_Down]
# Run the action
def take_action(action):
    Actions[action]()

def take_direction(direc):
    Directions[direc]()


class TackAction(threading.Thread):
    def __init__(self, threadID, name, direction, action):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.direction = direction
        self.action = action
        
    def run(self):
        take_direction(self.direction)
        take_action(self.action)