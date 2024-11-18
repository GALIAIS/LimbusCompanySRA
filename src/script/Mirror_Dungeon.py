# -*- coding: utf-8 -*-

# from src.common.utils import *
import src.common.config as cfg
from src.app.utils.ConfigManager import *
from src.common.actions import *


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
                navigate_to_mirror_dungeons()
                enter_wuthering_mirror()
                choose_random_ego_gift()
                confirm_ego_gift_info()
                team_formation()
                cfg.img_event.wait(timeout=20)
                if text_exists(cfg.img_src, r'正在探索第.+层') and not labels_exists(cfg.bboxes, Labels_ID['Drive']):
                    logger.info('结束初始任务')
                    cfg.img_event.clear()
                    mirror_only_flag = False
                    break

        while not self.mirror_pass_flag:
            logger.trace("开始镜牢4循环")
            retry_count = 0
            start_time = time.time()

            while retry_count < MAX_RETRIES:
                match True:
                    case _ if self.is_themes_pack_chosen():
                        logger.trace("Themes Pack选择")
                        choose_themes_pack()
                        retry_count += 1
                        if time.time() - start_time > TIMEOUT:
                            logger.warning("[选择主题包]超时，重新启动流程...")
                            break

                    case _ if self.is_ego_gift_chosen():
                        logger.trace("选择E.G.O饰品")
                        choose_ego_gift()
                        confirm_ego_gift_info()
                        retry_count += 1
                        if time.time() - start_time > TIMEOUT:
                            logger.warning("[选择E.G.O赠品]超时，重新启动流程...")
                            break

                    case _ if self.is_encounter_reward():
                        logger.trace("选择遭遇战奖励卡")
                        choose_encounter_reward_card()
                        retry_count += 1
                        if time.time() - start_time > TIMEOUT:
                            logger.warning("[遭遇战奖励]超时，重新启动流程...")
                            break

                    case _ if self.is_path_chosen():
                        logger.trace("开始路径选择...")
                        choose_path()
                        enter_event()
                        retry_count += 1
                        if time.time() - start_time > TIMEOUT:
                            logger.warning("[选择路径]超时，重新启动流程...")
                            break

                    case _ if self.is_shop():
                        logger.trace("进入商店界面")
                        shop_buy()
                        retry_count += 1
                        if time.time() - start_time > TIMEOUT:
                            logger.warning("[商店交易]超时，重新启动流程...")
                            break

                    case _ if self.is_battle_interface():
                        logger.trace("进入事件界面")
                        enter_event()
                        battle_choose_characters()
                        retry_count += 1
                        if time.time() - start_time > TIMEOUT:
                            logger.warning("[进入事件]超时，重新启动流程...")
                            break

                    case _ if self.is_in_battle():
                        logger.trace("开始战斗流程")
                        start_battle()
                        retry_count += 1
                        if time.time() - start_time > TIMEOUT:
                            logger.warning("[战斗]超时，重新启动流程...")
                            break

                    case _ if self.is_abnormality_encounter():
                        logger.trace("开始处理异想体遭遇事件")
                        abnormality_encounters_event()
                        retry_count += 1
                        if time.time() - start_time > TIMEOUT:
                            logger.warning("[处理异常遭遇]超时，重新启动流程...")
                            break

                    case _ if self.is_server_error():
                        logger.trace("服务器异常处理")
                        server_error()
                        retry_count += 1
                        if time.time() - start_time > TIMEOUT:
                            logger.warning("[服务器异常]超时，重新启动流程...")
                            break

                    case _ if self.is_victory():
                        logger.trace("镜牢结算验证")
                        check_mirror_completion()
                        retry_count += 1
                        if time.time() - start_time > TIMEOUT:
                            logger.warning("[镜牢结算]超时，重新启动流程...")
                            break

                    case _:
                        logger.warning("没有匹配的事件。")
                        continue

                if time.time() - start_time > TIMEOUT:
                    logger.warning("超时，重新启动流程...")
                    break

            self.mirror_pass_flag = check_mirror_completion()

    def is_themes_pack_chosen(self):
        cfg.img_event.wait(timeout=10)
        logger.info("判断选择主题包条件")
        try:
            if text_exists(cfg.img_src, r'选择.+层主题卡包'):
                return True
            return False
        finally:
            cfg.img_event.clear()

    def is_ego_gift_chosen(self):
        cfg.img_event.wait(timeout=10)
        logger.info("判断E.G.O饰品条件")
        try:
            if (text_exists(cfg.img_src, r'选择.+饰品') or text_exists(cfg.img_src,
                                                                       r'获得.+饰品.*')) and not text_exists(
                cfg.img_src, '探索完成') and not text_exists(cfg.img_src, '随机'):
                return True
            return False
        finally:
            cfg.img_event.clear()

    def is_encounter_reward(self):
        cfg.img_event.wait(timeout=10)
        cfg.bboxes_event.wait(timeout=10)
        logger.info("判断遭遇战奖励卡条件")
        try:
            if text_exists(cfg.img_src, '选择遭遇战奖励卡') and labels_exists(cfg.bboxes,
                                                                              Labels_ID['Encounter Reward Card']):
                return True
            return False
        finally:
            cfg.img_event.clear()
            cfg.bboxes_event.clear()

    def is_path_chosen(self):
        cfg.img_event.wait(timeout=10)
        cfg.bboxes_event.wait(timeout=10)
        logger.info("判断路径选择条件")
        mouse_scroll(-100)
        try:
            if text_exists(cfg.img_src, r'正在探索第.+层') and (
                    labels_exists(cfg.bboxes, Labels_ID['Battle Node']) or labels_exists(cfg.bboxes, Labels_ID[
                'Current Node'])) and not labels_exists(cfg.bboxes, Labels_ID['Enter']) and not text_exists(cfg.img_src,
                                                                                                            r'服务器发生错误.*'):
                return True
            return False
        finally:
            cfg.img_event.clear()
            cfg.bboxes_event.clear()

    def is_shop(self):
        cfg.img_event.wait(timeout=10)
        cfg.bboxes_event.wait(timeout=10)
        logger.info("判断商店界面条件")
        try:
            check_label_and_clickR(cfg.bboxes, 'Skip', clicks=5)
            # check_text_and_clickR(r'SKIP.*', clicks=3)
            cfg.img_event.wait(timeout=10)
            if text_exists(cfg.img_src, '商品列表') or text_exists(cfg.img_src, '治疗罪人'):
                cfg.img_event.clear()
                return True
            return False
        finally:
            cfg.img_event.clear()
            cfg.bboxes_event.clear()

    def is_battle_interface(self):
        cfg.img_event.wait(timeout=10)
        logger.info("判断进入战斗与角色选择界面条件")
        try:
            if (text_exists(cfg.img_src, '进入') or text_exists(cfg.img_src, '通关奖励') or text_exists(cfg.img_src,
                                                                                                        r'可参战.*') or text_exists(
                cfg.img_src, '开始战斗')) and not text_exists(cfg.img_src, '战斗胜利'):
                return True
            return False
        finally:
            cfg.img_event.clear()

    def is_in_battle(self):
        cfg.bboxes_event.wait(timeout=10)
        logger.info("判断战斗界面条件")
        try:
            if (labels_exists(cfg.bboxes, Labels_ID['Win Rate']) or labels_exists(cfg.bboxes,
                                                                                  Labels_ID['Damage']) or text_exists(
                cfg.img_src, '胜率') or text_exists(cfg.img_src, '伤害')) and not text_exists(cfg.img_src, '战斗胜利'):
                return True
            return False
        finally:
            cfg.bboxes_event.clear()

    def is_abnormality_encounter(self):
        cfg.img_event.wait(timeout=10)
        logger.info("判断异想体遭遇条件")
        try:
            check_text_and_clickR(r'SKIP.*', clicks=10)
            cfg.img_event.wait(timeout=10)
            if text_exists(cfg.img_src, r'SKIP.*') and not text_exists(
                    cfg.img_src, '商品列表') and not text_exists(cfg.img_src, '治疗罪人'):
                cfg.img_event.clear()
                return True
            return False
        finally:
            cfg.img_event.clear()

    def is_server_error(self):
        cfg.img_event.wait(timeout=10)
        logger.info("判断服务器异常条件")
        try:
            if text_exists(cfg.img_src, r'服务器发生错误.*'):
                return True
            return False
        finally:
            cfg.img_event.clear()

    def is_victory(self):
        cfg.img_event.wait(timeout=10)
        logger.info("判断镜牢胜利")
        try:
            if text_exists(cfg.img_src, '战斗胜利') or text_exists(cfg.img_src, '累计造成伤害') or text_exists(
                    cfg.img_src, '探索完成') or text_exists(cfg.img_src, '总进度'):
                return True
            return False
        finally:
            cfg.img_event.clear()

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


mirror_dungeon = Mirror_Wuthering()
