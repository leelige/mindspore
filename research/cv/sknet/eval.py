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
"""eval net"""
import argparse
from mindspore import context
from mindspore.common import set_seed
from mindspore.train.model import Model
from mindspore.train.serialization import load_checkpoint, load_param_into_net
from src.CrossEntropySmooth import CrossEntropySmooth

parser = argparse.ArgumentParser(description='Image classification')
parser.add_argument('--net', type=str, default="sknet50", help='Resnet Model, either sknet50')
parser.add_argument('--dataset', type=str, default="cifar10", help='Dataset, either cifar10 or imagenet2012')
parser.add_argument('--checkpoint_path', type=str, default="/path/to/sknet-90_195.ckpt", help='Checkpoint file path')
parser.add_argument('--dataset_path', type=str, default="/path/to/cifar10", help='Dataset path')
parser.add_argument('--device_target', type=str, default='Ascend',
                    help="Device target, support Ascend")
parser.add_argument('--device_id', type=int, default=0, help='Device num.')
args_opt = parser.parse_args()
set_seed(1)


if __name__ == '__main__':
    if args_opt.net == "sknet50":
        from src.sknet50 import sknet50 as sknet
        if args_opt.dataset == "cifar10":
            from src.config import config1 as config
            from src.dataset import create_dataset_cifar10 as create_dataset

    target = args_opt.device_target
    # init context
    context.set_context(mode=context.GRAPH_MODE, device_target=target, save_graphs=False)
    if target == "Ascend":
        device_id = int(args_opt.device_id)
        context.set_context(device_id=device_id)

    # create dataset
    dataset = create_dataset(dataset_path=args_opt.dataset_path, do_train=False, batch_size=config.batch_size,
                             target=target)
    step_size = dataset.get_dataset_size()
    print(step_size)
    # define net
    net = sknet(class_num=config.class_num)

    # load checkpoint
    param_dict = load_checkpoint(args_opt.checkpoint_path)
    load_param_into_net(net, param_dict)
    net.set_train(False)
    config.label_smooth_factor = 0.0
    loss = CrossEntropySmooth(sparse=True, reduction='mean',
                              smooth_factor=config.label_smooth_factor, num_classes=config.class_num)

    model = Model(net, loss_fn=loss, metrics={'top_1_accuracy', 'top_5_accuracy'})

    # eval model
    res = model.eval(dataset)
    print("result:", res, "ckpt=", args_opt.checkpoint_path)
