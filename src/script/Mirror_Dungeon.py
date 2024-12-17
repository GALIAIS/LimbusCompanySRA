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
    # EventType.EgoGiftChosen: lambda: (choose_ego_gift(), confirm_ego_gift_info(), other_event()),
    EventType.EgoGiftChosen: ego_gift_event,
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
class Mirror_Dungeon:
    loop_count: int = cfgm.get("Mirror_Dungeons.mirror_loop_count")
    current_count: int = 0
    mirror_switch: bool = cfgm.get("Mirror_Dungeons.mirror_switch")
    mirror_pass_flag: bool = None

    def start_mirror_dungeon(self):
        mirror_only_flag: bool = cfgm.get("Mirror_Dungeons.mirror_only_flag")
        TIMEOUT = 10 * 60
        MAX_RETRIES = 3
        logger.info("启动镜像迷宫流程")
        retries = 0

        while mirror_only_flag or retries >= MAX_RETRIES:
            img_event_wait = cfg.img_event.wait(timeout=10)
            bboxes_event_wait = cfg.bboxes_event.wait(timeout=10)

            if not img_event_wait or not bboxes_event_wait:
                logger.warning("图像或框选区域事件超时，跳过当前循环")
                retries += 1
                continue

            while True:
                if cfgm.get("Mirror_Dungeons.mirror_dungeons_choose") and labels_exists(cfg.bboxes, Labels_ID['Drive']):
                    match cfgm.get("Mirror_Dungeons.mirror_dungeons_choose.selected"):
                        case 1:
                            logger.info("启动梦中之镜流程")
                            if labels_exists(cfg.bboxes, Labels_ID['Drive']) and not text_exists(cfg.img_src,
                                                                                                 r'梦中之镜'):
                                cfg.img_event.clear()
                                cfg.bboxes_event.clear()
                                navigate_to_mirror_dungeons()
                        case 2:
                            logger.info("启动呼啸之镜流程")
                            if labels_exists(cfg.bboxes, Labels_ID['Drive']) and not text_exists(cfg.img_src,
                                                                                                 '呼啸之镜'):
                                cfg.img_event.clear()
                                cfg.bboxes_event.clear()
                                navigate_to_mirror_dungeons()
                        case _:
                            logger.warning("未知镜像迷宫选择，跳过当前循环")
                            break

                if text_exists(cfg.img_src, '呼啸之镜') or text_exists(cfg.img_src,
                                                                       '梦中之镜') or text_exists(
                    cfg.img_src, r'探索状态') or text_exists(cfg.img_src, '主题卡包图鉴'):
                    logger.info("进入镜牢")
                    cfg.img_event.clear()
                    enter_mirror_dungeons()
                    continue

                if text_exists(cfg.img_src, '播报员') and text_exists(cfg.img_src, '确认') and text_exists(cfg.img_src,
                                                                                                           '罪孽碎片'):
                    logger.info("队伍编成中")
                    cfg.img_event.clear()
                    team_formation()
                    continue

                if text_exists(cfg.img_src, '梦中的星之恩惠'):
                    logger.info("星之恩惠选择")
                    cfg.img_event.clear()
                    choose_grace_of_the_dreaming_star()
                    continue

                if text_exists(cfg.img_src, r'选择.+饰品') and text_list_exists(cfg.img_src,
                                                                                ['烧伤', '流血', '突刺', '打击']):
                    logger.info("选择初始饰品")
                    cfg.img_event.clear()
                    choose_random_ego_gift()
                    continue

                if (text_exists(cfg.img_src, 'E.G.O饰品信息') or text_exists(cfg.img_src,
                                                                             r'获得.+饰品.*')) and text_exists(
                    cfg.img_src, '确认'):
                    logger.info("确认饰品信息")
                    cfg.img_event.clear()
                    ego_gift_event()
                    continue

                if (text_exists(cfg.img_src, r'选择.+层主题卡包') and not labels_exists(cfg.bboxes, Labels_ID[
                    'Drive'])) or text_exists(cfg.img_src, r'正在探索第.+层'):
                    logger.info("结束初始任务")
                    cfg.img_event.clear()
                    mirror_only_flag = False
                    break

                break

            retries += 1
            if retries >= MAX_RETRIES:
                mirror_only_flag = False
                logger.warning("已达最大重试次数，退出初始事件流程")
                break

        while not self.mirror_pass_flag:
            logger.trace("开始镜牢循环")
            start_time = time.time()

            cfg.img_event.wait(timeout=5)
            cfg.bboxes_event.wait(timeout=5)

            try:
                while True:
                    event_type = None
                    match True:
                        case _ if self.is_path_chosen():
                            logger.info("路径选择事件")
                            event_type = EventType.PathChosen
                        case _ if self.is_battle_interface():
                            logger.info("战斗编队事件")
                            event_type = EventType.BattleInterface
                        case _ if self.is_in_battle():
                            logger.info("战斗事件")
                            event_type = EventType.InBattle
                        case _ if self.is_encounter_reward():
                            logger.info("遭遇奖励卡事件")
                            event_type = EventType.EncounterReward
                        case _ if self.is_themes_pack_chosen():
                            logger.info("主题包选择事件")
                            event_type = EventType.ThemesPackChosen
                        case _ if self.is_ego_gift_event():
                            logger.info("EgoGift事件")
                            event_type = EventType.EgoGiftChosen
                        case _ if self.is_shop():
                            logger.info("商店事件")
                            event_type = EventType.Shop
                        case _ if self.is_abnormality_encounter():
                            logger.info("异常遭遇事件")
                            event_type = EventType.AbnormalityEncounter
                        case _ if self.is_server_error():
                            logger.info("服务器错误事件")
                            event_type = EventType.ServerError
                        case _ if self.is_victory():
                            logger.info("胜利事件")
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
        return text_exists(cfg.img_src, r'选择.+层主题卡包')

    def is_ego_gift_event(self):
        return (
                text_exists(cfg.img_src, r'选择.+饰品')
                and text_exists(cfg.img_src, r'获得.+饰品.*')
                and text_exists(cfg.img_src, '拒绝饰品')
                and not text_exists(cfg.img_src, '探索完成')
        ) or (
                text_exists(cfg.img_src, r'获得.+饰品.*')
                and text_exists(cfg.img_src, r'正在探索第.+层')
        ) or (
                text_exists(cfg.img_src, r'获得.+饰品.*')
                and text_exists(cfg.img_src, '拒绝饰品')
                and text_exists(cfg.img_src, '选择')
        )

    def is_encounter_reward(self):
        return text_exists(cfg.img_src, '选择遭遇战奖励卡') and text_exists(cfg.img_src, '遭遇战奖励卡指南')

    def is_path_chosen(self):
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
        return (text_exists(cfg.img_src, r'商店') or text_exists(cfg.img_src, '结果')) and text_exists(cfg.img_src,
                                                                                                       '治疗罪人')

    def is_battle_interface(self):
        moveto(1380, 700)
        return (
                text_exists(cfg.img_src, '进入')
                or text_exists(cfg.img_src, '通关奖励')
                or text_exists(cfg.img_src, r'可参战.*')
                or text_exists(cfg.img_src, '开始战斗')
        ) and not text_exists(cfg.img_src, '战斗胜利')

    def is_in_battle(self):
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
        return (
                text_exists(cfg.img_src, r'SKIP.*')
                or text_exists(cfg.img_src, "决断")
                or labels_exists(cfg.bboxes, Labels_ID['Skip'])
                or text_exists(cfg.img_src, r".*选择后.+获得.+饰品")
                or text_exists(cfg.img_src, '判定成功')
        ) and not text_exists(cfg.img_src, '商店') and not text_exists(cfg.img_src, '治疗罪人')

    def is_server_error(self):
        return text_exists(cfg.img_src, r'服务器发生错误.*')

    def is_victory(self):
        return (
                text_exists(cfg.img_src, '战斗胜利')
                and text_exists(cfg.img_src, '累计造成伤害')
                and text_exists(cfg.img_src, '优秀员工')
        ) or (
                text_exists(cfg.img_src, '探索完成')
                and text_exists(cfg.img_src, '总进度')
        ) or text_exists(cfg.img_src, '探索结束奖励')


mw = Mirror_Dungeon()
