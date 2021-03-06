#!/bin/bash
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

# an simple tutorial as follows, more parameters can be setting
CONFIG=$1
DATA_PATH=$2

if [ $# != 2 ]
then
    echo "Usage: bash run_standalone_train_ascend.sh [YAML_CONFIG_PATH] [DATA_PATH]"
exit 1
fi

if [ ! -f $1 ]
then
    echo "error: config_path=$CONFIG is not a file."
exit 1
fi

if [ ! -d $2 ]
then
    echo "error: data_dir=$DATA_PATH is not a directory."
exit 1
fi

python ../train.py --config_path=$CONFIG  --data_dir=$DATA_PATH  > log.txt 2>&1 &
