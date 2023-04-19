# -*- coding: utf-8 -*-
import numpy as np
from tensorflow.keras.models import load_model
import tensorflow as tf
import os
import cv2
import time
import collections
import matplotlib.pyplot as plt
import random
from Model import Model
from DQN import DQN
from Agent import Agent
from ReplayMemory import ReplayMemory


import Tool.Helper
import Tool.Actions
from Tool.Helper import mean, is_end
from Tool.Actions import take_action, restart, play, take_direction, TackAction
from Tool.WindowsAPI import grab_screen
from Tool.PlayerData import Hp_getter
from Tool.UserInput import User
from Tool.FrameBuffer import FrameBuffer

# os.environ["CUDA_VISIBLE_DEVICES"] = '0'

# window_size = (0,0,1280, 720)
station_size = (5, 30, 1285, 750)

WIDTH = 400
HEIGHT = 200
ACTION_DIM = 5
MOVE_DIM = 6
FRAMEBUFFERSIZE = 4
INPUT_SHAPE = (FRAMEBUFFERSIZE, HEIGHT, WIDTH, 3)

MEMORY_SIZE = 256  # replay memory的大小，越大越占用内存
MEMORY_WARMUP_SIZE = 24  # replay_memory 里需要预存一些经验数据，再从里面sample一个batch的经验让agent去learn
BATCH_SIZE = 10  # 每次给agent learn的数据数量，从replay memory随机里sample一批数据出来
LEARNING_RATE = 0.00001  # 学习率
GAMMA = 0

action_name = ["Attack", "Jump", "Rush", "Skill_A", "Skill_S"]

move_name = ["Move_Left", "Move_Right", "Turn_Left", "Turn_Right", "Turn_Up", "Turn_Down"]

DELAY_REWARD = 1

def run_episode(hp, algorithm, agent, act_rmp_correct, move_rmp_correct, PASS_COUNT, paused, LAST_DONE):
    if LAST_DONE == 0 or LAST_DONE == 1:
        # 重新开始新游戏，返回城堡
        restart(hp.get_self_hp(),hp.get_enemies_count())
        # 从城堡出发
        play()
    else:
        Tool.Actions.Reload_Map()

    # learn while load game
    # for i in range(8):
    #     if (len(move_rmp_correct) > MEMORY_WARMUP_SIZE):
    #         print("move learning while load game")
    #         batch_station,batch_actions,batch_reward,batch_next_station,batch_done = move_rmp_correct.sample(BATCH_SIZE)
    #         algorithm.move_learn(batch_station,batch_actions,batch_reward,batch_next_station,batch_done)   

    #     if (len(act_rmp_correct) > MEMORY_WARMUP_SIZE):
    #         print("action learning while load game")
    #         batch_station,batch_actions,batch_reward,batch_next_station,batch_done = act_rmp_correct.sample(BATCH_SIZE)
    #         algorithm.act_learn(batch_station,batch_actions,batch_reward,batch_next_station,batch_done)

    done = 0 #1-玩家死亡 2-敌人清理完毕 3-超时未结束战斗 4-血量低于安全线
    step = 0
    total_reward = 0

    start_time = time.time()
    # Delay Reward
    DelayMoveReward = collections.deque(maxlen=DELAY_REWARD)
    DelayActReward = collections.deque(maxlen=DELAY_REWARD)
    DelayStation = collections.deque(maxlen=DELAY_REWARD + 1) # 1 more for next_station
    DelayActions = collections.deque(maxlen=DELAY_REWARD)
    DelayDirection = collections.deque(maxlen=DELAY_REWARD)
    
    # while True:
    #     boss_hp_value = hp.get_boss_hp()
    #     self_hp = hp.get_self_hp()
    #     if boss_hp_value > 800 and  boss_hp_value <= 900 and self_hp >= 1 and self_hp <= 9:
    #         break
        

    thread1 = FrameBuffer(1, "FrameBuffer", WIDTH, HEIGHT, maxlen=FRAMEBUFFERSIZE)
    thread1.start()

    # last_hornet_y = 0
    while True:
        step += 1
        # last_time = time.time()
        # no more than 10 mins
        # if time.time() - start_time > 600:
        #     break

        # in case of do not collect enough frames
        
        while(len(thread1.buffer) < FRAMEBUFFERSIZE):
            time.sleep(0.1)
        
        stations = thread1.get_buffer()
        #boss_hp_value = hp.get_boss_hp()
        enemies_count = hp.get_enemies_count()
        self_hp = hp.get_self_hp()
        #player_x, player_y = hp.get_play_location()
        #hornet_x, hornet_y = hp.get_hornet_location()
        #soul = hp.get_souls()

        # skul用不到，注释掉 begin
        # hornet_skill1 = False
        # if last_hornet_y > 32 and last_hornet_y < 32.5 and hornet_y > 32 and hornet_y < 32.5:
        #     hornet_skill1 = True
        # last_hornet_y = hornet_y
        # skul用不到，注释掉 end

        # 人工干预角色行为 begin
        move, action = agent.sample(stations)
        take_direction(move)
        take_action(action)
        # 人工干预角色行为 end
        
        # 下一帧行为随机产生
        # move = random.randint(0, 5)
        # action = random.randint(0, 4)
        # 执行随机动作
        # take_direction(move)
        # take_action(action)
        
        # print(time.time() - start_time, " action: ", action_name[action] , " move: ", move_name[move])
        # start_time = time.time()
        
        next_station = thread1.get_buffer()
        #next_boss_hp_value = hp.get_boss_hp()
        next_enemies_count = hp.get_enemies_count()
        next_self_hp = hp.get_self_hp()
        #next_player_x, next_player_y = hp.get_play_location()
        #next_hornet_x, next_hornet_y = hp.get_hornet_location()

        # get reward
        # move_reward = Tool.Helper.move_judge(self_hp, next_self_hp, player_x, next_player_x, hornet_x, next_hornet_x, move, hornet_skill1)
        move_reward = Tool.Helper.move_judge(self_hp, next_self_hp)
        # print(move_reward)
        act_reward, done = Tool.Helper.action_judge(self_hp, next_self_hp, enemies_count, next_enemies_count)
        # print(reward)
        # print( action_name[action], ", ", move_name[d], ", ", reward)
        tasktime = time.time() - start_time
        # 2分钟强制结束，敌人没有全部消灭，判定任务失败（角色死亡）
        if(tasktime >= 120):
            done = 3
            # 超时各扣十分
            move_reward = -10
            act_reward = -10
        print("用时: ", tasktime, " action: ", action_name[action] ,"act_reward: " ,act_reward, " move: ", move_name[move], "move_reward: ", move_reward)
        
        DelayMoveReward.append(move_reward)
        DelayActReward.append(act_reward)
        DelayStation.append(stations)
        DelayActions.append(action)
        DelayDirection.append(move)

        if len(DelayStation) >= DELAY_REWARD + 1:
            if DelayMoveReward[0] != 0:
                # print("move DelayStation[0]:", DelayStation[0])
                move_rmp_correct.append((DelayStation[0],DelayDirection[0],DelayMoveReward[0],DelayStation[1],done))
            # if DelayMoveReward[0] <= 0:
            #     move_rmp_wrong.append((DelayStation[0],DelayDirection[0],DelayMoveReward[0],DelayStation[1],done))

        if len(DelayStation) >= DELAY_REWARD + 1:
            if mean(DelayActReward) != 0:
                # print("act DelayStation[0]:", DelayStation[0])
                act_rmp_correct.append((DelayStation[0],DelayActions[0],mean(DelayActReward),DelayStation[1],done))
            # if mean(DelayActReward) <= 0:
            #     act_rmp_wrong.append((DelayStation[0],DelayActions[0],mean(DelayActReward),DelayStation[1],done))

        station = next_station
        self_hp = next_self_hp
        enemies_count = next_enemies_count
            

        # if (len(act_rmp) > MEMORY_WARMUP_SIZE and int(step/ACTION_SEQ) % LEARN_FREQ == 0):
        #     print("action learning")
        #     batch_station,batch_actions,batch_reward,batch_next_station,batch_done = act_rmp.sample(BATCH_SIZE)
        #     algorithm.act_learn(batch_station,batch_actions,batch_reward,batch_next_station,batch_done)

        total_reward += act_reward
        paused = Tool.Helper.pause_game(paused)
        LAST_DONE = done
        if done == 1 or done == 3 or done == 4:
            Tool.Actions.Nothing()
            break
        elif done == 2:
            PASS_COUNT += 1
            Tool.Actions.Nothing()
            time.sleep(3)
            break

    thread1.stop()

    # 暂停游戏开始学习
    Tool.Actions.Esc()
    
    for i in range(8):
        if (len(move_rmp_correct) > MEMORY_WARMUP_SIZE):
            print("move learning while end game")
            batch_station,batch_actions,batch_reward,batch_next_station,batch_done = move_rmp_correct.sample(BATCH_SIZE)
            algorithm.move_learn(batch_station,batch_actions,batch_reward,batch_next_station,batch_done)   

        if (len(act_rmp_correct) > MEMORY_WARMUP_SIZE):
            print("action learning while end game")
            batch_station,batch_actions,batch_reward,batch_next_station,batch_done = act_rmp_correct.sample(BATCH_SIZE)
            algorithm.act_learn(batch_station,batch_actions,batch_reward,batch_next_station,batch_done)
    # if (len(move_rmp_wrong) > MEMORY_WARMUP_SIZE):
    #     # print("move learning")
    #     batch_station,batch_actions,batch_reward,batch_next_station,batch_done = move_rmp_wrong.sample(1)
    #     algorithm.move_learn(batch_station,batch_actions,batch_reward,batch_next_station,batch_done)   

    # if (len(act_rmp_wrong) > MEMORY_WARMUP_SIZE):
    #     # print("action learning")
    #     batch_station,batch_actions,batch_reward,batch_next_station,batch_done = act_rmp_wrong.sample(1)
    #     algorithm.act_learn(batch_station,batch_actions,batch_reward,batch_next_station,batch_done)
    
    # 学习结束，取消暂停游戏
    Tool.Actions.Esc()
    return total_reward, step, PASS_COUNT, self_hp, LAST_DONE


if __name__ == '__main__':

    # In case of out of memory
    config = tf.compat.v1.ConfigProto(allow_soft_placement=True)
    config.gpu_options.allow_growth = True      #程序按需申请内存
    sess = tf.compat.v1.Session(config = config)

    
    total_remind_hp = 0

    move_rmp_correct = ReplayMemory(MEMORY_SIZE,file_name='./move_memory')         # experience pool
    act_rmp_correct = ReplayMemory(MEMORY_SIZE, file_name='./act_memory')         # experience pool
    
    # new model, if exit save file, load itf
    model = Model(INPUT_SHAPE, ACTION_DIM, MOVE_DIM)  

    # Hp counter
    hp = Hp_getter()


    model.load_model()
    algorithm = DQN(model, gamma=GAMMA, learnging_rate=LEARNING_RATE)
    agent = Agent(ACTION_DIM,algorithm,e_greed=0.65,e_greed_decrement=1e-6)
    
    # get user input, no need anymore
    # user = User()

    # paused at the begining
    paused = True
    paused = Tool.Helper.pause_game(paused)

    # 将开发者菜单调节至地图选择页面
    Tool.Actions.Init_DevMenu_T0_MapSelect()
    
    max_episode = 30000
    # 开始训练
    episode = 0
    PASS_COUNT = 0   # pass count
    LAST_DONE = 0
    while episode < max_episode:    # 训练max_episode个回合，test部分不计算入episode数量
        # 训练
        episode += 1     
        # if episode % 20 == 1:
        #     algorithm.replace_target()

        total_reward, total_step, PASS_COUNT, remind_hp, LAST_DONE = run_episode(hp, algorithm,agent,act_rmp_correct, move_rmp_correct, PASS_COUNT, paused, LAST_DONE)
        if episode % 10 == 1:
            model.save_mode()
        if episode % 5 == 0:
            move_rmp_correct.save(move_rmp_correct.file_name)
        if episode % 5 == 0:
            act_rmp_correct.save(act_rmp_correct.file_name)
        total_remind_hp += remind_hp
        print("Episode: ", episode, ", pass_count: " , PASS_COUNT, ", hp:", total_remind_hp / episode)

