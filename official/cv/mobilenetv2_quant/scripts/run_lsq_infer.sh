#!/usr/bin/env bash
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
if [ $# != 3 ]
then
    echo "Ascend: sh run_lsq_infer.sh [PLATFORM] [DATASET_PATH] [CHECKPOINT_PATH]"
exit 1
fi

# check dataset path
if [ ! -d $2 ] && [ ! -f $2 ]
then
    echo "error: DATASET_PATH=$2 is not a directory or file"
exit 1
fi

# check checkpoint file
if [ ! -f $3 ]
then
    echo "error: CHECKPOINT_PATH=$3 is not a file"
exit 1
fi

# set environment
BASEPATH=$(cd "`dirname $0`" || exit; pwd)
export DEVICE_ID=0
export RANK_ID=0
export RANK_SIZE=1
if [ -d "../eval" ];
then
    rm -rf ../eval
fi
mkdir ../eval
cd ../eval || exit

# launch
python ${BASEPATH}/../eval.py \
        --device_target=$1 \
        --dataset_path=$2 \
        --checkpoint_path=$3 \
        --optim_option="LEARNED_SCALE" \
        &> infer.log &  # dataset val folder path
