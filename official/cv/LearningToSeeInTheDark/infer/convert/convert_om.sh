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

air_path=$1
om_path=$2

export install_path=/usr/local/Ascend/

export ASCEND_ATC_PATH=${install_path}/atc
export LD_LIBRARY_PATH=${install_path}/atc/lib64:$LD_LIBRARY_PATH
export PATH=/usr/local/python3.7.5/bin:${install_path}/atc/ccec_compiler/bin:${install_path}/atc/bin:$PATH
export PYTHONPATH=${install_path}/atc/python/site-packages:${install_path}/latest/atc/python/site-packages/auto_tune.egg/auto_tune:${install_path}/atc/python/site-packages/schedule_search.egg
export ASCEND_OPP_PATH=${install_path}/opp

echo "Input AIR file path: ${air_path}"
echo "Output OM file path: ${om_path}"

atc --input_format=NCHW \
    --framework=1 \
    --model="${air_path}" \
    --output="${om_path}" \
    --log=debug \
    --output_type=FP32 \
    --soc_version=Ascend310 \
    --input_shape="input:1,4,1424,2128"
