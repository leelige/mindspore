# Copyright 2021 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================
"""learning rate generator"""
import math
import numpy as np

def get_lr(lr_init, lr_decay_rate, num_epoch_per_decay, total_epochs, steps_per_epoch, is_stair=False):
    """
    generate learning rate array

    Args:
       lr_init(float): init learning rate
       lr_decay_rate (float):
       total_epochs(int): total epoch of training
       steps_per_epoch(int): steps of one epoch
       is_stair(bool): If `True` decay the learning rate at discrete intervals (default=False)

    Returns:
       learning_rate, learning rate numpy array
    """
    lr_each_step = []
    total_steps = steps_per_epoch * total_epochs
    decay_steps = steps_per_epoch * num_epoch_per_decay
    for i in range(total_steps):
        p = i/decay_steps
        if is_stair:
            p = math.floor(p)
        lr_each_step.append(lr_init * math.pow(lr_decay_rate, p))
    learning_rate = np.array(lr_each_step).astype(np.float32)
    return learning_rate

def get_lr_basic(lr_init, total_epochs, steps_per_epoch, is_stair=False):
    """
    generate basic learning rate array

    Args:
       lr_init(float): init learning rate
       total_epochs(int): total epochs of training
       steps_per_epoch(int): steps of one epoch
       is_stair(bool): If `True` decay the learning rate at discrete intervals (default=False)

    Returns:
       learning_rate, learning rate numpy array
    """
    lr_each_step = []
    total_steps = steps_per_epoch * total_epochs
    for i in range(total_steps):
        lr = lr_init - lr_init * (i) / (total_steps)
        lr_each_step.append(lr)
    learning_rate = np.array(lr_each_step).astype(np.float32)
    return learning_rate

def linear_warmup_lr(current_step, warmup_steps, base_lr, init_lr):
    """Linear learning rate"""
    lr_inc = (float(base_lr) - float(init_lr)) / float(warmup_steps)
    lr = float(init_lr) + lr_inc * current_step
    return lr

def warmup_cosine_annealing_lr(lr, max_epoch, steps_per_epoch, warmup_epochs=5, T_max=150, eta_min=0.0):
    """ Cosine annealing learning rate"""
    base_lr = lr
    warmup_init_lr = 0
    total_steps = int(max_epoch * steps_per_epoch)
    warmup_steps = int(warmup_epochs * steps_per_epoch)

    lr_each_step = []
    for i in range(total_steps):
        last_epoch = i // steps_per_epoch
        if i < warmup_steps:
            lr = linear_warmup_lr(i + 1, warmup_steps, base_lr, warmup_init_lr)
        else:
            lr = eta_min + (base_lr - eta_min) * (1. + math.cos(math.pi*last_epoch / T_max)) / 2
        lr_each_step.append(lr)

    return np.array(lr_each_step).astype(np.float32)
