# -*- coding: utf-8 -*-
import time
from enum import Enum, auto
from typing import Callable
from src.common.actions import *
from src.common.utils import *


class EventType(Enum):
    ThemesPackChosen = auto()
    EgoGiftChosen = auto()
    EncounterReward = auto()
    PathChosen = auto()
    Shop = auto()
    BattleInterface = auto()
    InBattle = auto()
    AbnormalityEncounter = auto()
    ServerError = auto()
    Victory = auto()


EventHandler = Callable[[], None]

event_handlers = {
    EventType.ThemesPackChosen: choose_themes_pack,
    EventType.EgoGiftChosen: lambda: (choose_ego_gift(), confirm_ego_gift_info(), other_event()),
    EventType.EncounterReward: choose_encounter_reward_card,
    EventType.PathChosen: lambda: (choose_path(), enter_event()),
    EventType.Shop: shop_buy,
    EventType.BattleInterface: lambda: (enter_event(), battle_choose_characters()),
    EventType.InBattle: start_battle,
    EventType.AbnormalityEncounter: abnormality_encounters_event,
    EventType.ServerError: server_error,
    EventType.Victory: check_mirror_completion,
}


@define
class Mirror_Wuthering:
    """镜牢4流程脚本"""
    loop_count: int = int(cfgm.get("Mirror_Dungeons.mirror_loop_count"))
    current_count: int = 0
    mirror_switch: bool = cfgm.get("Mirror_Dungeons.mirror_switch")
    mirror_pass_flag: bool = None

    def start_mirror_wuthering(self):
        """开始镜牢4流程"""
        mirror_only_flag: bool = cfgm.get("Mirror_Dungeons.mirror_only_flag")
        TIMEOUT = 10 * 60
        MAX_RETRIES = 3
        logger.info("启动镜牢4流程")
        RETRIES = 0

        while mirror_only_flag:
            img_event_wait = cfg.img_event.wait(timeout=10)
            bboxes_event_wait = cfg.bboxes_event.wait(timeout=10)

            if not img_event_wait or not bboxes_event_wait:
                logger.warning("图像或框选区域事件超时，跳过当前循环")
                continue

            while True:
                cfg.img_event.wait(timeout=10)
                cfg.bboxes_event.wait(timeout=10)
                if labels_exists(cfg.bboxes, Labels_ID['Drive']) and not text_exists(cfg.img_src, '呼啸之镜'):
                    cfg.img_event.clear()
                    cfg.bboxes_event.clear()
                    navigate_to_mirror_dungeons()
                    continue

                cfg.img_event.wait(timeout=10)
                if text_exists(cfg.img_src, '呼啸之镜') or text_exists(cfg.img_src, r'探索状态'):
                    cfg.img_event.clear()
                    enter_wuthering_mirror()
                    continue

                cfg.img_event.wait(timeout=10)
                if text_exists(cfg.img_src, r'选择.+饰品') and not text_exists(cfg.img_src, r'获得.+饰品.*'):
                    cfg.img_event.clear()
                    choose_random_ego_gift()
                    continue

                cfg.img_event.wait(timeout=10)
                if (text_exists(cfg.img_src, 'E.G.O饰品信息') or text_exists(cfg.img_src,
                                                                             r'获得.+饰品.*')) and text_exists(
                    cfg.img_src, '确认'):
                    cfg.img_event.clear()
                    confirm_ego_gift_info()
                    continue

                cfg.img_event.wait(timeout=10)
                if text_exists(cfg.img_src, '播报员') and text_exists(cfg.img_src, '确认') and text_exists(cfg.img_src,
                                                                                                           '罪孽碎片'):
                    cfg.img_event.clear()
                    team_formation()
                    continue

                cfg.img_event.wait(timeout=10)
                if (text_exists(cfg.img_src, r'选择.+层主题卡包') and not labels_exists(cfg.bboxes, Labels_ID[
                    'Drive'])) or text_exists(cfg.img_src, r'正在探索第.+层'):
                    logger.info('结束初始任务')
                    cfg.img_event.clear()
                    mirror_only_flag = False
                    break

        while not self.mirror_pass_flag:
            logger.trace("开始镜牢4循环")
            start_time = time.time()

            cfg.img_event.wait(timeout=5)
            cfg.bboxes_event.wait(timeout=5)

            try:
                while True:
                    event_type = None
                    match True:
                        case _ if self.is_path_chosen():
                            event_type = EventType.PathChosen
                        case _ if self.is_battle_interface():
                            event_type = EventType.BattleInterface
                        case _ if self.is_in_battle():
                            event_type = EventType.InBattle
                        case _ if self.is_encounter_reward():
                            event_type = EventType.EncounterReward
                        case _ if self.is_themes_pack_chosen():
                            event_type = EventType.ThemesPackChosen
                        case _ if self.is_ego_gift_chosen():
                            event_type = EventType.EgoGiftChosen
                        case _ if self.is_shop():
                            event_type = EventType.Shop
                        case _ if self.is_abnormality_encounter():
                            event_type = EventType.AbnormalityEncounter
                        case _ if self.is_server_error():
                            event_type = EventType.ServerError
                        case _ if self.is_victory():
                            event_type = EventType.Victory
                            self.mirror_pass_flag = event_handlers[event_type]()
                            break
                        case _:
                            logger.warning("没有匹配的事件")
                            other_event()
                            continue

                    if event_type in event_handlers:
                        logger.trace(f"处理事件: {event_type}")
                        event_handlers[event_type]()
                    else:
                        logger.error(f"未找到事件处理函数: {event_type}")
                        break

                    continue

            finally:
                cfg.img_event.clear()
                cfg.bboxes_event.clear()

            if time.time() - start_time > TIMEOUT:
                logger.warning("超时，重新启动流程...")
                break

        logger.info("镜牢4流程结束")

    def clear_events(self):
        cfg.img_event.clear()
        cfg.bboxes_event.clear()

    def prepare(self):
        cfg.img_event.wait(timeout=10)
        cfg.bboxes_event.wait(timeout=10)

    def check_condition(self, *conditions):
        for condition in conditions:
            if condition():
                return True
        return False

    def is_themes_pack_chosen(self):
        logger.info("判断选择主题包条件")
        return text_exists(cfg.img_src, r'选择.+层主题卡包')

    def is_ego_gift_chosen(self):
        logger.info("判断E.G.O饰品条件")
        return (
                text_exists(cfg.img_src, r'选择.+饰品')
                and text_exists(cfg.img_src, r'获得.+饰品.*')
                and text_exists(cfg.img_src, '拒绝饰品')
                and not text_exists(cfg.img_src, '探索完成')
        ) or (
                text_exists(cfg.img_src, r'获得.+饰品.*')
                and text_exists(cfg.img_src, r'正在探索第.+层')
        )

    def is_encounter_reward(self):
        logger.info("判断遭遇战奖励卡条件")
        return text_exists(cfg.img_src, '选择遭遇战奖励卡')

    def is_path_chosen(self):
        logger.info("判断路径选择条件")
        if (text_exists(cfg.img_src, r'正在探索.*')
                or (
                        labels_exists(cfg.bboxes, Labels_ID['Safe Node'])
                        or labels_exists(cfg.bboxes, Labels_ID['Current Node'])
                        or labels_exists(cfg.bboxes, Labels_ID['Battle Node'])
                )):
            mouse_scroll(-200)
        return (
                text_exists(cfg.img_src, r'正在探索.*')
                and (
                        labels_exists(cfg.bboxes, Labels_ID['Safe Node'])
                        or labels_exists(cfg.bboxes, Labels_ID['Current Node'])
                        or labels_exists(cfg.bboxes, Labels_ID['Battle Node'])
                )
                and not labels_exists(cfg.bboxes, Labels_ID['Enter'])
                and not text_exists(cfg.img_src, r'服务器发生错误.*')
        )

    def is_shop(self):
        logger.info("判断商店界面条件")
        if text_exists(cfg.img_src, r'SKIP.*') or text_exists(cfg.img_src, r"\d{2}:\d{2}:\d{2}:\d{2}"):
            check_text_and_clickR(r'SKIP.*', 10)
        return text_exists(cfg.img_src, r'商品列表.*') or text_exists(cfg.img_src, '治疗罪人') or text_exists(
            cfg.img_src, '结果')

    def is_battle_interface(self):
        logger.info("判断进入战斗与角色选择界面条件")
        return (
                text_exists(cfg.img_src, '进入')
                or text_exists(cfg.img_src, '通关奖励')
                or text_exists(cfg.img_src, r'可参战.*')
                or text_exists(cfg.img_src, '开始战斗')
        ) and not text_exists(cfg.img_src, '战斗胜利')

    def is_in_battle(self):
        logger.info("判断战斗界面条件")
        return (
                labels_exists(cfg.bboxes, Labels_ID['Win Rate'])
                and labels_exists(cfg.bboxes, Labels_ID['Damage'])
                and (
                        text_exists(cfg.img_src, '胜率')
                        or text_exists(cfg.img_src, '伤害')
                )
                and not text_exists(cfg.img_src, '战斗胜利')
        )

    def is_abnormality_encounter(self):
        logger.info("判断异想体遭遇条件")
        check_text_and_clickR(r'SKIP.*', 10)
        return (
                text_exists(cfg.img_src, r'SKIP.*')
                or text_exists(cfg.img_src, "决断")
                or labels_exists(cfg.bboxes, Labels_ID['Skip'])
                or text_exists(cfg.img_src, r".*选择后.+获得.+饰品")
                or text_exists(cfg.img_src, '判定成功')
        ) and not text_exists(cfg.img_src, '商品列表') and not text_exists(cfg.img_src, '治疗罪人')

    def is_server_error(self):
        logger.info("判断服务器异常条件")
        return text_exists(cfg.img_src, r'服务器发生错误.*')

    def is_victory(self):
        logger.info("判断镜牢胜利")
        return (
                text_exists(cfg.img_src, '战斗胜利')
                and text_exists(cfg.img_src, '累计造成伤害')
                and text_exists(cfg.img_src, '优秀员工')
        ) or (
                text_exists(cfg.img_src, '探索完成')
                and text_exists(cfg.img_src, '总进度')
        ) or text_exists(cfg.img_src, '探索结束奖励')

    # def run(self):
    #     """循环执行镜牢4流程"""
    #     logger.info(f"开始执行镜牢4流程，循环次数: {self.loop_count}")
    #     for _ in range(self.loop_count):
    #         if not self.mirror_switch:
    #             logger.info("镜牢4流程未开启")
    #             break
    #         try:
    #             self.mirror_pass_flag = False
    #             self.start_mirror_wuthering()
    #             self.current_count += 1
    #             logger.info(f"已完成第 {self.current_count} 次镜牢4")
    #             logger.info(f"即将进入第 {self.current_count + 1} 次镜牢4")
    #         except Exception as e:
    #             logger.error(f"镜牢4流程出错: {e}")
    #             logger.info("尝试回到主界面...")
    #             return_to_main_menu()
    #
    #     logger.info(f"开始执行EXP副本流程，循环次数: {self.loop_count}")
    #     for _ in range(int(cfgm.get("Luxcavation.exp_loop_count"))):
    #         if not cfgm.get("Luxcavation.exp_switch"):
    #             logger.info("EXP副本流程未开启")
    #             break
    #         try:
    #             self.exp_pass_flag = False
    #             self.start_mirror_wuthering()
    #             self.current_count += 1
    #             logger.info(f"已完成第 {self.current_count} 次EXP副本")
    #             logger.info(f"即将进入第 {self.current_count + 1} 次EXP副本")
    #         except Exception as e:
    #             logger.error(f"EXP副本流程出错: {e}")
    #             logger.info("尝试回到主界面...")
    #             return_to_main_menu()
    #
    #     logger.info(f"开始执行Thread副本流程，循环次数: {self.loop_count}")
    #     for _ in range(int(cfgm.get("Luxcavation.thread_loop_count"))):
    #         if not cfgm.get("Luxcavation.thread_switch"):
    #             logger.info("Thread副本流程未开启")
    #             break
    #         try:
    #             self.thread_pass_flag = False
    #             self.start_mirror_wuthering()
    #             self.current_count += 1
    #             logger.info(f"已完成第 {self.current_count} 次Thread副本")
    #             logger.info(f"即将进入第 {self.current_count + 1} 次Thread副本")
    #         except Exception as e:
    #             logger.error(f"Thread副本流程出错: {e}")
    #             logger.info("尝试回到主界面...")
    #             return_to_main_menu()


mw = Mirror_Wuthering()
