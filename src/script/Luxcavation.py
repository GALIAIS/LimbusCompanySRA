# -*- coding: utf-8 -*-

from src.common.utils import *
from src.common.actions import *


@define
class Luxcavation:
    def Luxcavation_EXP(self):
        cfg.bboxes_event.wait(timeout=10)
        while labels_exists(cfg.bboxes, Labels_ID['EXP']) and labels_exists(cfg.bboxes, Labels_ID['Thread']):
            cfg.bboxes_event.clear()
            if cfgm.get("Luxcavation.exp_switch"):
                while cfgm.get("Luxcavation.exp_choose.exp_loop_count") >= current_loop_count:
                    cfg.bboxes_event.wait(timeout=10)
                    check_label_and_click(cfg.bboxes, 'EXP')
                    cfg.bboxes_event.clear()

                current_loop_count = 1

    def Luxcavation_Thread(self):
        thread_switch: bool = False
        thread_choose: int = 0


luxcavation = Luxcavation()
