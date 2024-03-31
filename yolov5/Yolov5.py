import torch
import torch.nn as nn
import yaml
import numpy as np
from yolov5.models.common import Conv, C3, SPPF, Concat
from yolov5.models.yolo import Detect
from torch.nn import Upsample
from yolov5.utils.general import non_max_suppression

device = 'cuda:0'


def from_numpy(x):
    return torch.from_numpy(x) if isinstance(x, np.ndarray) else x

model_config_text = """
backbone:
  # [from, number, module, args]
  [[-1, 1, Conv, [64, 6, 2, 2]],  # 0-P1/2
   [-1, 1, Conv, [128, 3, 2]],  # 1-P2/4
   [-1, 3, C3, [128]],
   [-1, 1, Conv, [256, 3, 2]],  # 3-P3/8
   [-1, 6, C3, [256]],
   [-1, 1, Conv, [512, 3, 2]],  # 5-P4/16
   [-1, 9, C3, [512]],
   [-1, 1, Conv, [768, 3, 2]],  # 7-P5/32
   [-1, 3, C3, [768]],
   [-1, 1, Conv, [1024, 3, 2]],  # 9-P6/64
   [-1, 3, C3, [1024]],
   [-1, 1, SPPF, [1024, 5]],  # 11
  ]

# YOLOv5 v6.0 head
head:
  [[-1, 1, Conv, [768, 1, 1]],
   [-1, 1, nn.Upsample, [None, 2, 'nearest']],
   [[-1, 8], 1, Concat, [1]],  # cat backbone P5
   [-1, 3, C3, [768, False]],  # 15

   [-1, 1, Conv, [512, 1, 1]],
   [-1, 1, nn.Upsample, [None, 2, 'nearest']],
   [[-1, 6], 1, Concat, [1]],  # cat backbone P4
   [-1, 3, C3, [512, False]],  # 19

   [-1, 1, Conv, [256, 1, 1]],
   [-1, 1, nn.Upsample, [None, 2, 'nearest']],
   [[-1, 4], 1, Concat, [1]],  # cat backbone P3
   [-1, 3, C3, [256, False]],  # 23 (P3/8-small)

   [-1, 1, Conv, [256, 3, 2]],
   [[-1, 20], 1, Concat, [1]],  # cat head P4
   [-1, 3, C3, [512, False]],  # 26 (P4/16-medium)

   [-1, 1, Conv, [512, 3, 2]],
   [[-1, 16], 1, Concat, [1]],  # cat head P5
   [-1, 3, C3, [768, False]],  # 29 (P5/32-large)

   [-1, 1, Conv, [768, 3, 2]],
   [[-1, 12], 1, Concat, [1]],  # cat head P6
   [-1, 3, C3, [1024, False]],  # 32 (P6/64-xlarge)

   [[23, 26, 29, 32], 1, Detect, [nc, anchors]],  # Detect(P3, P4, P5, P6)
  ]
"""

param_config_text = """
nc: 80  # number of classes
depth_multiple: 0.33  # model depth multiple
width_multiple: 0.50  # layer channel multiple
anchors:
  - [19,27,  44,40,  38,94]  # P3/8
  - [96,68,  86,152,  180,137]  # P4/16
  - [140,301,  303,264,  238,542]  # P5/32
  - [436,615,  739,380,  925,792]  # P6/64
"""


model_config = yaml.load(model_config_text, Loader=yaml.FullLoader)
param_config = yaml.load(param_config_text, Loader=yaml.FullLoader)

submodule_list = []
module_map = {"Conv" : Conv, "C3" : C3, "SPPF" : SPPF, "Concat" : Concat, "nn.Upsample" : Upsample, "Detect" : Detect}

no_channel_module = ["Concat", "nn.Upsample"]
depth_multiple_module = ["C3"]

# model_multiple = {"n" : [0.33, 0.25], "s" : [0.33, 0.5], "m" : [0.67, 0.75], "l" : [1.0, 1.0], "x" : [1.33, 1.25]}
H, W, C = 320, 320, 3

a = 0
index = 0

for part_name, parts  in model_config.items():
    for part in parts:
        # print("P" + str(index))
        _, depth, module_name, arg = part

        if module_name == "Conv":
            arg[0] = round(arg[0] * param_config["width_multiple"])
            temp_module = Conv(C, *arg)
            C = arg[0]

        elif module_name == "C3":
            arg[0] = round(arg[0] * param_config["width_multiple"])
            temp_module = C3(C, arg[0], n = max(1, int(round(depth * param_config["depth_multiple"], 1))))
            # print("n : ", max(1, int(round(depth * param_config["depth_multiple"], 1))))
            C = arg[0]
            
        elif module_name == "SPPF":
            arg[0] = round(arg[0] * param_config["width_multiple"])
            temp_module = SPPF(C, *arg)
            C = arg[0]

        elif module_name == "Concat":
            temp_module = Concat(*arg)
            C *= 2

        elif module_name == "nn.Upsample":
            temp_module = nn.Upsample(size = None, scale_factor = arg[1], mode = arg[2])

        elif module_name == "Detect":
            temp_module = Detect(param_config["nc"], param_config["anchors"], (round(256 * param_config["width_multiple"]), round(512 * param_config["width_multiple"]), round(768 * param_config["width_multiple"]), round(1024 * param_config["width_multiple"])))

        # for name, param in temp_module.state_dict().items():
        #     print(name)

        # print(max(1, int(round(depth * param_config["depth_multiple"], 1))))

        submodule_list.append(temp_module)

        a += len(temp_module.state_dict())
        index += 1

# print(a)


i = 0
for submodule in submodule_list:
    submodule.load_state_dict(torch.load(f"yolov5/weights/P{i}.pt"))
    submodule.eval()
    i += 1

submodule_list[-1].stride = torch.tensor([8, 16, 32, 64])

class P1(nn.Module):
    def __init__(self):
        super().__init__()
        self.M0 = submodule_list[0]
        self.M1 = submodule_list[1]
        self.M2 = submodule_list[2]
        self.M3 = submodule_list[3]
        self.M4 = submodule_list[4]
        self.M5 = submodule_list[5]
        self.M6 = submodule_list[6]
        self.M7 = submodule_list[7]
        self.M8 = submodule_list[8]
        self.M9 = submodule_list[9]
        self.M10 = submodule_list[10]
        self.M11 = submodule_list[11]

    def forward(self, x):
        x1 = self.M0(x)
        x2 = self.M1(x1)
        x3 = self.M2(x2)
        x4 = self.M3(x3)
        x5 = self.M4(x4)
        x6 = self.M5(x5)
        x7 = self.M6(x6)
        x8 = self.M7(x7)
        x9 = self.M8(x8)
        x10 = self.M9(x9)
        x11 = self.M10(x10)
        x12 = self.M11(x11)

        return [x5, x7, x9, x12]

class P2(nn.Module):
    def __init__(self):
        super().__init__()
        self.M12 = submodule_list[12]
        self.M13 = submodule_list[13]
        self.M14 = submodule_list[14]
        self.M15 = submodule_list[15]
        self.M16 = submodule_list[16]
        self.M17 = submodule_list[17]
        self.M18 = submodule_list[18]
        self.M19 = submodule_list[19]
        self.M20 = submodule_list[20]
        self.M21 = submodule_list[21]
        self.M22 = submodule_list[22]
        self.M23 = submodule_list[23]

    def forward(self, x):
        x5, x7, x9, x12 = x
        x13 = self.M12(x12)
        x14 = self.M13(x13)
        x15 = self.M14([x14, x9])
        x16 = self.M15(x15)
        x17 = self.M16(x16)
        x18 = self.M17(x17)
        x19 = self.M18([x18, x7])
        x20 = self.M19(x19)
        x21 = self.M20(x20)
        x22 = self.M21(x21)
        x23 = self.M22([x22, x5])
        x24 = self.M23(x23)

        return [x13, x17, x21, x24]
        

class P3(nn.Module):
    def __init__(self):
        super().__init__()
        self.M24 = submodule_list[24]
        self.M25 = submodule_list[25]
        self.M26 = submodule_list[26]
        self.M27 = submodule_list[27]
        self.M28 = submodule_list[28]
        self.M29 = submodule_list[29]
        self.M30 = submodule_list[30]
        self.M31 = submodule_list[31]
        self.M32 = submodule_list[32]


    def forward(self, x):
        x13, x17, x21, x24 = x
        x25 = self.M24(x24)
        x26 = self.M25([x25, x21])
        x27 = self.M26(x26)
        x28 = self.M27(x27)
        x29 = self.M28([x28, x17])
        x30 = self.M29(x29)
        x31 = self.M30(x30)
        x32 = self.M31([x31, x13])
        x33 = self.M32(x32)


        return [x24, x27, x30, x33]

class P4(nn.Module):
    def __init__(self):
        super().__init__()
        self.M33 = submodule_list[33]

    def forward(self, x):
        x24, x27, x30, x33 = x

        x34 = self.M33([x24, x27, x30, x33])

        pred = from_numpy(x34[0]) if len(x34) == 1 else [from_numpy(x) for x in x34]
        pred = non_max_suppression(pred[0], 0.3)

        return pred
    

# p1 = P1()
# p2 = P2()
# p3 = P3()
# p4 = P4()

# def warm_up():
#     dummy = torch.rand(1, 3, 320, 320)
#     x = p1(dummy)
#     x = p2(x)
#     x = p3(x)
#     x = p4(x)
    
# warm_up()