# Copyright 2020 Huawei Technologies Co., Ltd
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
"""Evaluate MobilenetV2 on ImageNet"""

import os
import argparse

from mindspore import context
from mindspore import nn
from mindspore.train.model import Model
from mindspore.train.serialization import load_checkpoint, load_param_into_net
from mindspore.compression.common import QuantDtype
from mindspore.compression.quant import QuantizationAwareTraining
from mindspore.compression.quant.quantizer import OptimizeOption
from src.mobilenetV2 import mobilenetV2
from src.mobilenetv2_mix_quant import mobilenetv2_mix_quant
from src.dataset import create_dataset
from src.config import config_ascend_quant, config_gpu_quant, config_lsq_ascend_quant, config_lsq_gpu_quant

parser = argparse.ArgumentParser(description='Image classification')
parser.add_argument('--checkpoint_path', type=str, default=None, help='Checkpoint file path')
parser.add_argument('--dataset_path', type=str, default=None, help='Dataset path')
parser.add_argument('--device_target', type=str, default=None, help='Run device target')
parser.add_argument('--optim_option', type=str, default="QAT", help='OptimizeOption')
args_opt = parser.parse_args()

if __name__ == '__main__':
    config_device_target = None
    device_id = int(os.getenv('DEVICE_ID'))
    if args_opt.device_target == "Ascend":
        if args_opt.optim_option == "LEARNED_SCALE":
            config_device_target = config_lsq_ascend_quant
        else:
            config_device_target = config_ascend_quant
            symmetric_list = [True, False]
        context.set_context(mode=context.GRAPH_MODE, device_target="Ascend",
                            device_id=device_id, save_graphs=False)
    elif args_opt.device_target == "GPU":
        if args_opt.optim_option == "LEARNED_SCALE":
            config_device_target = config_lsq_gpu_quant
        else:
            config_device_target = config_gpu_quant
            symmetric_list = [False, False]
        context.set_context(mode=context.GRAPH_MODE, device_target="GPU",
                            device_id=device_id, save_graphs=False)
    else:
        raise ValueError("Unsupported device target: {}.".format(args_opt.device_target))


    if args_opt.optim_option == "LEARNED_SCALE":
        # define fusion network
        network = mobilenetv2_mix_quant(num_classes=config_device_target.num_classes)
        # convert fusion network to quantization aware network
        quant_optim_otions = OptimizeOption.LEARNED_SCALE
        quantizer = QuantizationAwareTraining(bn_fold=True,
                                              per_channel=[True, False],
                                              symmetric=[True, True],
                                              narrow_range=[True, True],
                                              quant_dtype=(QuantDtype.INT4, QuantDtype.INT8),
                                              freeze_bn=0,
                                              quant_delay=0,
                                              one_conv_fold=True,
                                              optimize_option=quant_optim_otions)
    else:
        # define fusion network
        network = mobilenetV2(num_classes=config_device_target.num_classes)
        # convert fusion network to quantization aware network
        quantizer = QuantizationAwareTraining(bn_fold=True,
                                              per_channel=[True, False],
                                              symmetric=symmetric_list)
    network = quantizer.quantize(network)

    # define network loss
    loss = nn.SoftmaxCrossEntropyWithLogits(sparse=True, reduction='mean')

    # define dataset
    dataset = create_dataset(dataset_path=args_opt.dataset_path,
                             do_train=False,
                             config=config_device_target,
                             device_target=args_opt.device_target,
                             batch_size=config_device_target.batch_size)
    step_size = dataset.get_dataset_size()

    # load checkpoint
    if args_opt.checkpoint_path:
        param_dict = load_checkpoint(args_opt.checkpoint_path)
        not_load_param = load_param_into_net(network, param_dict)
        if not_load_param:
            raise ValueError("Load param into net fail!")
    network.set_train(False)

    # define model
    model = Model(network, loss_fn=loss, metrics={'acc'})

    print("============== Starting Validation ==============")
    res = model.eval(dataset)
    print("result:", res, "ckpt=", args_opt.checkpoint_path)
    print("============== End Validation ==============")
