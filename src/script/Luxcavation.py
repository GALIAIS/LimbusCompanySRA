# -*- coding: utf-8 -*-

from src.common.utils import *
from src.common.actions import cfgm


@define
class Luxcavation:
    def Luxcavation_EXP(self):
        exp_selected: str = str(cfgm.get("Luxcavation.exp_choose.selected"))
        exp_choose: str = cfgm.get("Luxcavation.exp_choose")
        while True:
            cfg.img_event.wait(timeout=10)
            cfg.bboxes_event.wait(timeout=10)
            if (labels_exists(cfg.bboxes, Labels_ID['Drive'])
                    and (not text_exists(cfg.img_src, '经验')
                         or not text_exists(cfg.img_src, '纺锤'))):
                self.navigate_to_luxcavation()
                continue
            cfg.img_event.clear()
            cfg.bboxes_event.clear()

            if text_exists(cfg.img_src, '经验') and text_exists(cfg.img_src, r'经验采光.*'):
                check_model_click(cfg.bboxes, exp_choose[exp_selected], Labels_ID['Enter'])
                cfg.img_event.clear()
                cfg.bboxes_event.clear()
                continue
            cfg.img_event.clear()
            cfg.bboxes_event.clear()

            if not text_exists(cfg.img_src, '经验') and not text_exists(cfg.img_src, '纺锤'):
                self.battle_choose_characters()
                self.start_battle()
                self.check_mirror_completion()
                cfg.img_event.clear()
                cfg.bboxes_event.clear()
                break
            cfg.img_event.clear()
            cfg.bboxes_event.clear()

    def Luxcavation_Thread(self):
        thread_selected: str = str(cfgm.get("Luxcavation.thread_choose.selected"))
        thread_choose: str = cfgm.get("Luxcavation.thread_choose")
        while True:
            cfg.img_event.wait(timeout=10)
            cfg.bboxes_event.wait(timeout=10)
            if (labels_exists(cfg.bboxes, Labels_ID['Drive'])
                    and (not text_exists(cfg.img_src, '经验')
                         or not text_exists(cfg.img_src, '纺锤'))):
                self.navigate_to_luxcavation()
                continue
            cfg.img_event.clear()
            cfg.bboxes_event.clear()

            if text_exists(cfg.img_src, '纺锤') and not text_exists(cfg.img_src, r'经验采光.*'):
                check_model_click(cfg.bboxes, thread_choose[thread_selected], Labels_ID['Enter'])
                cfg.img_event.clear()
                cfg.bboxes_event.clear()
                continue
            cfg.img_event.clear()
            cfg.bboxes_event.clear()

            if not text_exists(cfg.img_src, '经验') and not text_exists(cfg.img_src, '纺锤'):
                self.battle_choose_characters()
                self.start_battle()
                self.check_mirror_completion()
                cfg.img_event.clear()
                cfg.bboxes_event.clear()
                break
            cfg.img_event.clear()
            cfg.bboxes_event.clear()

    def start_battle(self):
        """战斗事件流程"""
        win_rate_clicked = False

        while True:
            cfg.img_event.wait(timeout=10)
            cfg.bboxes_event.wait(timeout=10)
            if (not text_exists(cfg.img_src, r'.*TART') or not labels_exists(cfg.bboxes,
                                                                             Labels_ID['Start'])) and labels_exists(
                cfg.bboxes,
                Labels_ID['Win Rate']):
                check_label_and_clickR(cfg.bboxes, 'Start')
                cfg.img_event.clear()
                cfg.bboxes_event.clear()
                win_rate_clicked = False
            cfg.img_event.clear()
            cfg.bboxes_event.clear()

            cfg.img_event.wait(timeout=10)
            cfg.bboxes_event.wait(timeout=10)
            if (text_exists(cfg.img_src, '胜率') or labels_exists(cfg.bboxes,
                                                                  Labels_ID['Win Rate'])) and not win_rate_clicked:
                check_label_and_clickR(cfg.bboxes, 'Win Rate')
                cfg.img_event.clear()
                cfg.bboxes_event.clear()
                win_rate_clicked = True
                time.sleep(2)

            cfg.img_event.wait(timeout=10)
            cfg.bboxes_event.wait(timeout=10)
            if text_exists(cfg.img_src, r'.*TART') or labels_exists(cfg.bboxes, Labels_ID['Start']):
                check_label_and_clickR(cfg.bboxes, 'Start')
                cfg.img_event.clear()
                cfg.bboxes_event.clear()
                win_rate_clicked = False
                time.sleep(5)

                cfg.img_event.wait(timeout=10)
                if not (text_exists(cfg.img_src, r'胜率.*') or text_exists(cfg.img_src, r'伤害.*')):
                    cfg.img_event.clear()
                    continue

            cfg.img_event.wait(timeout=10)
            cfg.bboxes_event.wait(timeout=10)
            if not labels_exists(cfg.bboxes, Labels_ID['Win Rate']) and not labels_exists(cfg.bboxes,
                                                                                          Labels_ID['Damage']) and (
                    text_exists(cfg.img_src, '选择遭遇战奖励卡')
                    or text_exists(cfg.img_src, r'正在探索.*')
                    or text_exists(cfg.img_src, r'选择.+饰品')
                    or text_exists(cfg.img_src, r'获得.+饰品.*')
                    or text_exists(cfg.img_src, '战斗胜利')
                    or text_exists(cfg.img_src, '累计造成伤害')
                    or text_exists(cfg.img_src, '通关奖励')):
                cfg.img_event.clear()
                cfg.bboxes_event.clear()
                break
            cfg.img_event.clear()
            cfg.bboxes_event.clear()

        logger.info("结束战斗流程")

    def navigate_to_luxcavation(self):
        logger.info("判断是否处于驾驶席界面...")
        while True:
            cfg.bboxes_event.wait(timeout=10)
            if labels_exists(cfg.bboxes, Labels_ID['Drive']) and not labels_exists(cfg.bboxes,
                                                                                   Labels_ID['Luxcavation']):
                check_label_and_click(cfg.bboxes, 'Drive')
                cfg.bboxes_event.clear()
                logger.info("已切换到驾驶席界面")
                continue
            cfg.bboxes_event.clear()

            cfg.bboxes_event.wait(timeout=10)
            if labels_exists(cfg.bboxes, Labels_ID['Mirror Dungeon']) and labels_exists(cfg.bboxes,
                                                                                        Labels_ID['Luxcavation']):
                check_label_and_click(cfg.bboxes, 'Luxcavation')
                cfg.bboxes_event.clear()
                logger.info("已切换到采光界面")
                continue
            cfg.bboxes_event.clear()

            cfg.bboxes_event.wait(timeout=10)
            if labels_exists(cfg.bboxes, Labels_ID['EXP']) and labels_exists(cfg.bboxes, Labels_ID['Thread']):
                cfg.bboxes_event.clear()
                break

    def battle_choose_characters(self):
        """参战角色选择"""
        while True:
            cfg.img_event.wait(timeout=5)
            cfg.bboxes_event.wait(timeout=5)
            if not text_exists(cfg.img_src, '6/6') and text_exists(cfg.img_src, '开始战斗'):
                # check_label_and_click(cfg.bboxes, 'Start')
                cfg.img_event.clear()
                cfg.bboxes_event.clear()
                continue
            else:
                check_label_and_click(cfg.bboxes, 'Start')
                cfg.img_event.clear()
                cfg.bboxes_event.clear()

            cfg.img_event.wait(timeout=5)
            cfg.bboxes_event.wait(timeout=5)
            if not text_exists(cfg.img_src, '6/6') and not text_exists(cfg.img_src, '开始战斗'):
                cfg.img_event.clear()
                cfg.bboxes_event.clear()
                break
            cfg.img_event.clear()
            cfg.bboxes_event.clear()

        logger.info("结束参战角色选择界面检测")

    def check_mirror_completion(self) -> bool:
        cfg.img_event.wait(timeout=10)
        if not any(text_exists(cfg.img_src, pattern) for pattern in [
            '战斗胜利', '累计造成伤害', '探索完成', '总进度', '探索结束奖励', r'经理等级提升.*']):
            cfg.img_event.clear()
            return False
        cfg.img_event.clear()

        while True:
            cfg.img_event.wait(timeout=10)
            cfg.bboxes_event.wait(timeout=10)
            if text_exists(cfg.img_src, '战斗胜利') and text_exists(cfg.img_src, '累计造成伤害') and text_exists(
                    cfg.img_src, '通关奖励'):
                check_label_and_click(cfg.bboxes, 'Confirm')
                cfg.img_event.clear()
                cfg.bboxes_event.clear()
                continue
            cfg.img_event.clear()
            cfg.bboxes_event.clear()

            if text_exists(cfg.img_src, r'经理等级提升.*') and text_exists(cfg.img_src, '累计造成伤害'):
                check_label_and_click(cfg.bboxes, 'Confirm')
                cfg.img_event.clear()
                cfg.bboxes_event.clear()
                continue
            cfg.img_event.clear()
            cfg.bboxes_event.clear()

            cfg.img_event.wait(timeout=5)
            if not any(text_exists(cfg.img_src, pattern) for pattern in [
                '战斗胜利', '累计造成伤害', r'经理等级提升.*']):
                cfg.img_event.clear()
                break
            cfg.img_event.clear()


luxcavation = Luxcavation()
