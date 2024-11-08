# -*- coding: utf-8 -*-
import sys
import time

sys.path.insert(0, '../')
from src.common.utils import *


@define
class Mirror_Wuthering:
    """镜牢4流程脚本"""
    loop_count: int = cfg.mirror_loop_count
    current_count: int = 0
    mirror_switch: bool = cfg.mirror_switch
    mirror_pass_flag: bool = None
    mirror_only_flag: bool = False
    first_run: bool = True

    def start_mirror_wuthering(self):
        """开始镜牢4流程"""
        TIMEOUT = 10 * 60
        MAX_RETRIES = 3
        logger.info("启动镜牢4流程")

        while self.mirror_only_flag:
            img_event_wait = cfg.img_event.wait(timeout=10)
            bboxes_event_wait = cfg.bboxes_event.wait(timeout=10)

            if not img_event_wait or not bboxes_event_wait:
                logger.warning("图像或框选区域事件超时，跳过当前循环")
                continue

            if self.first_run:
                self.navigate_to_mirror_dungeons()
                self.enter_wuthering_mirror()
                self.entry_random_choose_ego_gift()
                self.confirm_ego_gift_info()
                self.team_formation()

                self.first_run = False
                self.mirror_only_flag = False

                # cfg.img_event.wait(timeout=10)
                # if text_exists(cfg.img_src, r'选择.+层主题卡包'):
                #     self.choose_themes_pack()
                #     self.mirror_only_flag = False
                #     cfg.img_event.clear()

        while not self.mirror_pass_flag:
            logger.trace("开始镜牢4循环")
            retry_count = 0
            start_time = time.time()

            while retry_count < MAX_RETRIES:
                match True:
                    case _ if self.is_themes_pack_chosen():
                        logger.trace("Themes Pack选择")
                        self.choose_themes_pack()
                        retry_count += 1
                        if time.time() - start_time > TIMEOUT:
                            logger.warning("[选择主题包]超时，重新启动流程...")
                            break

                    case _ if self.is_ego_gift_chosen():
                        logger.trace("选择E.G.O饰品")
                        self.choose_ego_gift()
                        self.confirm_ego_gift_info()
                        retry_count += 1
                        if time.time() - start_time > TIMEOUT:
                            logger.warning("[选择E.G.O赠品]超时，重新启动流程...")
                            break

                    case _ if self.is_encounter_reward():
                        logger.trace("选择遭遇战奖励卡")
                        self.choose_encounter_reward_card()
                        retry_count += 1
                        if time.time() - start_time > TIMEOUT:
                            logger.warning("[遭遇战奖励]超时，重新启动流程...")
                            break

                    case _ if self.is_path_chosen():
                        logger.trace("开始路径选择...")
                        self.choose_path()
                        self.enter_event()
                        retry_count += 1
                        if time.time() - start_time > TIMEOUT:
                            logger.warning("[选择路径]超时，重新启动流程...")
                            break

                    case _ if self.is_shop():
                        logger.trace("进入商店界面")
                        self.shop_buy()
                        retry_count += 1
                        if time.time() - start_time > TIMEOUT:
                            logger.warning("[商店交易]超时，重新启动流程...")
                            break

                    case _ if self.is_battle_interface():
                        logger.trace("进入事件界面")
                        self.enter_event()
                        self.battle_choose_characters()
                        retry_count += 1
                        if time.time() - start_time > TIMEOUT:
                            logger.warning("[进入事件]超时，重新启动流程...")
                            break

                    case _ if self.is_in_battle():
                        logger.trace("开始战斗流程")
                        self.start_battle()
                        retry_count += 1
                        if time.time() - start_time > TIMEOUT:
                            logger.warning("[战斗]超时，重新启动流程...")
                            break

                    case _ if self.is_abnormality_encounter():
                        logger.trace("开始处理异想体遭遇事件")
                        self.abnormality_encounters_event()
                        retry_count += 1
                        if time.time() - start_time > TIMEOUT:
                            logger.warning("[处理异常遭遇]超时，重新启动流程...")
                            break

                    case _ if self.is_server_error():
                        logger.trace("服务器异常处理")
                        self.server_error()
                        retry_count += 1
                        if time.time() - start_time > TIMEOUT:
                            logger.warning("[服务器异常]超时，重新启动流程...")
                            break

                    case _ if self.is_victory():
                        logger.trace("镜牢结算验证")
                        self.check_mirror_completion()
                        retry_count += 1
                        if time.time() - start_time > TIMEOUT:
                            logger.warning("[镜牢结算]超时，重新启动流程...")
                            break

                    case _:
                        logger.warning("没有匹配的事件，跳出循环。")
                        break

                if time.time() - start_time > TIMEOUT:
                    logger.warning("超时，重新启动流程...")
                    break

            self.mirror_pass_flag = self.check_mirror_completion()

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
                cfg.img_src, '探索完成'):
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
            if text_exists(cfg.img_src, '商品列表') or text_exists(cfg.img_src, '治疗罪人') or text_exists(cfg.img_src,
                                                                                                           '编队'):
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
            if (text_exists(cfg.img_src, r'SKIP.*') or text_exists(cfg.img_src,
                                                                   r"\d{2}:\d{2}:\d{2}:\d{2}")) and not text_exists(
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

    def navigate_to_mirror_dungeons(self):
        """导航到镜像迷宫界面"""
        logger.info("判断是否处于驾驶席界面...")

        cfg.bboxes_event.wait(timeout=10)
        while labels_exists(cfg.bboxes, Labels_ID['Drive']) and not text_exists(cfg.img_src, '镜像迷宫'):
            check_label_and_click(cfg.bboxes, 'Drive')
            logger.info("已切换到驾驶席界面")
            cfg.img_event.wait(timeout=10)
            cfg.img_event.clear()
            cfg.bboxes_event.wait(timeout=10)
            cfg.bboxes_event.clear()
        logger.info("结束驾驶席界面检测")

        logger.info("判断是否处于镜像迷宫界面...")
        cfg.bboxes_event.wait(timeout=10)
        while labels_exists(cfg.bboxes, Labels_ID['Mirror Dungeon']) and labels_exists(cfg.bboxes,
                                                                                       Labels_ID['Luxcavation']):
            logger.info("正在尝试进入镜像迷宫~")

            check_label_and_click(cfg.bboxes, 'Mirror Dungeon')

            cfg.img_event.wait(timeout=10)
            if text_exists(cfg.img_src, '呼啸之镜'):
                logger.info("已进入镜像迷宫")
            cfg.img_event.clear()
            cfg.bboxes_event.clear()
        logger.info("结束镜像迷宫界面检测")

    def enter_wuthering_mirror(self):
        """进入呼啸之镜"""
        logger.info("判断是否进入呼啸之镜...")

        if not cfg.img_event.wait(timeout=10):
            logger.warning("初始图像更新超时，退出流程")
            return

        while text_exists(cfg.img_src, '呼啸之镜') or text_exists(cfg.img_src, r'探索状态'):
            logger.info("正在尝试进入呼啸之镜~")

            if not cfg.bboxes_event.wait(timeout=10):
                logger.warning("坐标更新超时，退出流程")
                return

            check_label_and_click(cfg.bboxes, 'Mirror Dungeon')

            cfg.img_event.clear()
            cfg.bboxes_event.clear()

            cfg.img_event.wait(timeout=10)
            cfg.bboxes_event.wait(timeout=10)
            if text_exists(cfg.img_src, '迷宫进度'):
                check_label_and_clickR(cfg.bboxes, 'Resume')
                check_text_and_clickR("继续")
                logger.info("已恢复迷宫进度")
                cfg.img_event.clear()
                cfg.bboxes_event.clear()
            elif text_exists(cfg.img_src, r'是否进入呼啸之镜.*'):
                check_text_and_clickR("确认")
                check_label_and_click(cfg.bboxes, 'Confirm')
                logger.info("已进入呼啸之镜")
                cfg.img_event.clear()
                cfg.bboxes_event.clear()

            cfg.img_event.wait(timeout=10)
            cfg.bboxes_event.wait(timeout=10)
            if text_exists(cfg.img_src, '当前进度已过期。请领取您的奖励。'):
                check_label_and_click(cfg.bboxes, 'Confirm')
                logger.info("确认领取奖励")
                cfg.img_event.clear()
                cfg.bboxes_event.clear()
            elif text_exists(cfg.img_src, '探索结束奖励') and not text_exists(cfg.img_src, '8/8'):
                check_label_and_click(cfg.bboxes, 'Give Up')
                logger.info("放弃奖励")
                cfg.img_event.clear()
                cfg.bboxes_event.clear()
            elif text_exists(cfg.img_src, r'要在不领取奖励的情况下结束探索吗.*'):
                check_label_and_click(cfg.bboxes, 'Confirm')
                logger.info("放弃奖励")
                cfg.img_event.clear()
                cfg.bboxes_event.clear()
            elif text_exists(cfg.img_src, '探索结束奖励') and text_exists(cfg.img_src, '8/8'):
                check_label_and_click(cfg.bboxes, 'Confirm')
                logger.info("已领取探索奖励")
                cfg.img_event.clear()
                cfg.bboxes_event.clear()

        logger.info("结束呼啸之镜界面检测")

    def entry_random_choose_ego_gift(self):
        """随机选择E.G.O饰品"""
        logger.info("随机E.G.O饰品选择")

        cfg.img_event.wait(timeout=10)
        while text_exists(cfg.img_src, r'选择.+饰品') and text_exists(cfg.img_src, '随机'):
            cfg.img_event.clear()

            cfg.img_event.wait(timeout=10)
            if text_exists(cfg.img_src, r'选择.+饰品'):
                cfg.bboxes_event.wait(timeout=10)
                check_label_and_click(cfg.bboxes, 'E.G.O Gift')
                cfg.bboxes_event.clear()

                cfg.img_event.wait(timeout=10)
                if text_exists(cfg.img_src, '0/2'):
                    cfg.bboxes_event.wait(timeout=10)
                    result_check = check_text_in_model(cfg.bboxes, '？？？')
                    click_center_of_bbox(result_check)
                    cfg.bboxes_event.clear()

                    cfg.bboxes_event.wait(timeout=10)
                    check_label_and_click(cfg.bboxes, 'Confirm')
                    cfg.bboxes_event.clear()
        logger.info("结束随机E.G.O饰品界面检测")

    def choose_ego_gift(self):
        """选择E.G.O饰品"""
        # logger.info("选择E.G.O饰品")

        cfg.img_event.wait(timeout=10)
        while text_exists(cfg.img_src, r'选择.+饰品') and text_exists(cfg.img_src, r'获得.+饰品.*'):
            cfg.img_event.clear()

            cfg.img_event.wait(timeout=10)
            if text_exists(cfg.img_src, r'选择.+饰品'):
                cfg.bboxes_event.wait(timeout=10)
                check_label_and_click(cfg.bboxes, 'E.G.O Gift')
                cfg.img_event.clear()
                cfg.bboxes_event.clear()

                cfg.img_event.wait(timeout=10)
                if text_exists(cfg.img_src, r'选择.+饰品'):
                    cfg.bboxes_event.wait(timeout=10)
                    check_label_and_click(cfg.bboxes, 'Confirm')
                    check_text_and_click('确认')
                    cfg.img_event.clear()
                    cfg.bboxes_event.clear()
        logger.info("结束选择E.G.O饰品界面检测")

    def choose_encounter_reward_card(self):
        """选择遭遇战奖励卡"""
        # logger.info("选择遭遇战奖励卡")

        while text_exists(cfg.img_src, '选择遭遇战奖励卡') and labels_exists(cfg.bboxes,
                                                                             Labels_ID['Encounter Reward Card']):
            cfg.img_event.wait(timeout=10)
            if cfg.img_event.is_set():
                cfg.img_event.clear()

                if text_exists(cfg.img_src, r'可选择0.*'):
                    cfg.bboxes_event.wait(timeout=10)
                    if cfg.bboxes_event.is_set():
                        check_label_and_click(cfg.bboxes, 'Encounter Reward Card')
                        cfg.bboxes_event.clear()

                cfg.img_event.wait(timeout=10)
                if text_exists(cfg.img_src, r'可选择1.*'):
                    cfg.bboxes_event.wait(timeout=10)
                    if cfg.bboxes_event.is_set():
                        check_label_and_click(cfg.bboxes, 'Confirm')
                        cfg.bboxes_event.clear()

        logger.info("结束选择遭遇战奖励卡界面检测")

    def confirm_ego_gift_info(self):
        """确认E.G.O饰品信息"""
        logger.info("检测E.G.O饰品信息界面")

        cfg.img_event.wait(timeout=10)
        while (text_exists(cfg.img_src, 'E.G.O饰品信息') or text_exists(cfg.img_src,
                                                                        r'获得E.G.O饰品.*')) and text_exists(
            cfg.img_src, '确认'):
            cfg.img_event.clear()

            cfg.img_event.wait(timeout=10)
            if text_exists(cfg.img_src, 'E.G.O饰品信息') or text_exists(cfg.img_src, r'获得E.G.O饰品.*'):
                cfg.bboxes_event.wait(timeout=10)
                check_text_and_click(r'选择.+饰品')
                check_label_and_click(cfg.bboxes, 'Confirm')
                cfg.img_event.clear()
                cfg.bboxes_event.clear()
                break
        logger.info("结束E.G.O饰品信息界面检测")

    def team_formation(self):
        """编队"""
        logger.info("进入初始编队界面")

        try:
            if not cfg.img_event.wait(timeout=10):
                logger.warning("未能获取到最新图像数据，超时")
                return
            while text_exists(cfg.img_src, '播报员') and text_exists(cfg.img_src, '确认') and text_exists(cfg.img_src,
                                                                                                          '罪孽碎片'):
                if not cfg.img_event.wait(timeout=10):
                    logger.warning("等待图像数据超时，重新尝试")
                    continue
                if text_exists(cfg.img_src, r'编队.*') and text_exists(cfg.img_src, '罪孽碎片'):
                    if not cfg.bboxes_event.wait(timeout=10):
                        logger.warning("等待框选区域超时，跳过当前操作")
                        continue
                    check_label_and_click(cfg.bboxes, 'Confirm')
                    cfg.bboxes_event.clear()
                    logger.info("确认初始编队")
                cfg.img_event.clear()
        except Exception as e:
            logger.error(f"编队操作发生异常: {e}")
        logger.info("结束初始编队界面检测")

    def choose_themes_pack(self):
        """选择主题卡包"""
        # logger.info("Themes Pack选择")

        cfg.img_event.wait(timeout=10)
        while text_exists(cfg.img_src, r'选择.+层主题卡包'):
            cfg.img_event.clear()

            cfg.img_event.wait(timeout=10)
            if text_exists(cfg.img_src, r'.*主题卡包'):
                cfg.bboxes_event.wait(timeout=10)
                check_label_and_drag(cfg.bboxes, 'Themes Pack')
                cfg.bboxes_event.clear()

        logger.info("结束Themes Pack界面检测")

    def choose_path(self):
        """选择路径"""
        # logger.info("开始选择路径...")

        NODE_PRIORITY = {
            Labels_ID.get('Safe Node', None): 4.0,
            Labels_ID.get('Event Node', None): 3.0,
            Labels_ID.get('Battle Node', None): 2.0,
            Labels_ID.get('Current Node', None): 1.0,
            Labels_ID.get('End Node', None): 0.0
        }

        try_count = 0

        cfg.img_event.wait(timeout=10)
        mouse_scroll(-100)
        while text_exists(cfg.img_src, r'正在探索第.+层') and not labels_exists(cfg.bboxes, Labels_ID['Enter']):
            cfg.img_event.clear()
            mouse_scroll(-100)

            cfg.bboxes_event.wait(timeout=10)
            bboxes = cfg.bboxes

            available_nodes = [(bbox, NODE_PRIORITY[label_id]) for bbox in bboxes for label_id in NODE_PRIORITY if
                               label_id is not None and label_exists(bbox, label_id)]
            cfg.bboxes_event.clear()

            if not available_nodes:
                logger.warning("未找到可点击的节点")
                break

            node_labels = {node[0][5]: node[1] for node in available_nodes}
            if len(node_labels) == 2 and Labels_ID['Current Node'] in node_labels and Labels_ID[
                'End Node'] in node_labels:
                if try_count < 3:
                    node_id = Labels_ID['End Node']
                    try_count += 1
                    logger.info(f"仅发现Current Node和End Node，尝试第{try_count}次优先选择End Node")
                else:
                    node_id = Labels_ID['Current Node']
                    logger.info("End Node尝试3次失败，选择Current Node")
                    try_count = 0
            else:
                try_count = 0
                selected_node = \
                    max(available_nodes,
                        key=lambda x: x[1] if x[1] > 0.0 else min(available_nodes, key=lambda x: x[1])[1])[
                        0]
                node_id = selected_node[5] if len(selected_node) > 5 else None
                if node_id is None:
                    logger.error("节点数据结构不符合预期，无法获取 node_id")
                    break

            logger.info(f"选择节点: {Labels_ID.inverse[node_id]}")
            check_label_id_and_click(cfg.bboxes, node_id)
            time.sleep(1)

        logger.info("结束路径选择")

    def shop_buy(self):
        """商店购买"""
        # logger.info("商店购买界面")

        cfg.img_event.wait(timeout=10)
        while text_exists(cfg.img_src, '商品列表') or text_exists(cfg.img_src, '治疗罪人') or text_exists(cfg.img_src,
                                                                                                          '编队') or text_exists(
            cfg.img_src, '强化饰品') or text_exists(cfg.img_src, '合成饰品'):
            cfg.img_event.clear()
            check_text_and_clickR(r'SKIP.*', clicks=2)

            cfg.img_event.wait(timeout=10)
            cfg.bboxes_event.wait(timeout=10)
            if text_exists(cfg.img_src, '治疗罪人') or labels_exists(cfg.bboxes, Labels_ID['Heal Sinner']):
                check_text_and_click('治疗罪人')
                move_mouse_to_center()
                cfg.img_event.clear()
                cfg.bboxes_event.clear()

            cfg.img_event.wait(timeout=10)
            if text_exists(cfg.img_src, r'.*让全体罪人坐在椅子上休息.*') or text_exists(cfg.img_src,
                                                                                        r"全体罪人恢复.+体力.+理智值") or text_exists(
                cfg.img_src, '选择能量饮料') or text_exists(cfg.img_src, '购买成功'):
                # check_text_and_click(r'.*让全体罪人坐在椅子上休息.*')
                # check_text_and_click(r'.*选择能量饮料')
                check_text_and_click(r'全体罪人恢复.+体力.+理智值')
                cfg.img_event.clear()

            cfg.img_event.wait(timeout=10)
            if text_exists(cfg.img_src, '选择看上去疲倦的罪人') or text_exists(cfg.img_src, r'让谁休息比较好呢.*'):
                check_text_and_click(r'选择看上去疲倦的罪人')
                cfg.img_event.clear()

            cfg.img_event.wait(timeout=10)
            if text_exists(cfg.img_src, '购买成功'):
                cfg.bboxes_event.wait(timeout=10)
                check_label_and_click(cfg.bboxes, 'Confirm')
                cfg.img_event.clear()
                cfg.bboxes_event.clear()

            cfg.img_event.wait(timeout=10)
            if text_exists(cfg.img_src, r'SOLD.+OUT') and text_exists(cfg.img_src, '离开'):
                cfg.bboxes_event.wait(timeout=10)
                check_text_and_click('离开')
                check_label_and_click(cfg.bboxes, 'Leava')
                cfg.img_event.clear()
                cfg.bboxes_event.clear()

            cfg.img_event.wait(timeout=10)
            cfg.bboxes_event.wait(timeout=10)
            if text_exists(cfg.img_src, '售卖饰品') and not text_exists(cfg.img_src, '治疗罪人'):
                check_label_and_click(cfg.bboxes, 'Leava')
                cfg.img_event.clear()
                cfg.bboxes_event.clear()

            cfg.img_event.wait(timeout=10)
            if text_exists(cfg.img_src, r'要离开休息点吗.*'):
                cfg.bboxes_event.wait(timeout=10)
                check_text_and_click('确认')
                check_label_and_click(cfg.bboxes, 'Confirm')
                cfg.img_event.clear()
                cfg.bboxes_event.clear()

            cfg.img_event.wait(timeout=10)
            if text_exists(cfg.img_src, r'要离开商店吗.*'):
                cfg.bboxes_event.wait(timeout=10)
                check_text_and_click('确认')
                check_label_and_click(cfg.bboxes, 'Confirm')
                cfg.img_event.clear()
                cfg.bboxes_event.clear()

        logger.info("结束商店购买界面检测")

    def enter_event(self):
        """进入事件界面"""
        # logger.info("进入战斗界面")

        cfg.img_event.wait(timeout=10)
        while text_exists(cfg.img_src, '通关奖励') or text_exists(cfg.img_src, '进入'):
            cfg.img_event.clear()

            cfg.img_event.wait(timeout=10)
            if text_exists(cfg.img_src, '进入'):
                cfg.bboxes_event.wait(timeout=10)
                check_label_and_click(cfg.bboxes, 'Enter')
                cfg.bboxes_event.clear()

        logger.info("结束进入事件界面检测")

    def battle_choose_characters(self):
        """参战角色选择"""
        logger.info("参战角色选择界面")

        cfg.img_event.wait(timeout=10)
        while text_exists(cfg.img_src, r'可参战.*') and text_exists(cfg.img_src, '开始战斗'):
            cfg.img_event.clear()

            logger.info("自动选择角色有时间写,现在即将进入战斗...")
            cfg.img_event.wait(timeout=10)
            if not text_exists(cfg.img_src, '6/6'):
                cfg.bboxes_event.wait(timeout=10)
                check_label_and_click(cfg.bboxes, 'Start')
                cfg.bboxes_event.clear()
            else:
                cfg.bboxes_event.wait(timeout=10)
                check_label_and_click(cfg.bboxes, 'Start')
                cfg.bboxes_event.clear()

        logger.info("结束参战角色选择界面检测")

    def start_battle(self):
        """战斗事件流程"""
        # logger.info("开始战斗流程")
        win_rate_clicked = False

        cfg.img_event.wait(timeout=10)
        while labels_exists(cfg.bboxes, Labels_ID['Win Rate']) or labels_exists(cfg.bboxes, Labels_ID['Damage']):
            if (text_exists(cfg.img_src, '胜率') or labels_exists(cfg.bboxes,
                                                                  Labels_ID['Win Rate'])) and not win_rate_clicked:

                cfg.bboxes_event.wait(timeout=10)
                if cfg.bboxes_event.is_set():
                    check_label_and_clickR(cfg.bboxes, 'Win Rate')
                    win_rate_clicked = True
                    cfg.bboxes_event.clear()

            elif text_exists(cfg.img_src, r'.*TART') or labels_exists(cfg.bboxes, Labels_ID['Start']):
                cfg.bboxes_event.wait(timeout=10)
                if cfg.bboxes_event.is_set():
                    check_label_and_clickR(cfg.bboxes, 'Start')
                    win_rate_clicked = False
                    cfg.bboxes_event.clear()
        cfg.img_event.clear()

        logger.info("结束战斗流程")

    def abnormality_encounters_event(self):
        """异想体遭遇事件流程"""
        # logger.info("开始处理异想体遭遇事件")

        max_attempts = 3
        attempts = 0

        event_text_conditions = [
            r".*成功后.+获得.+饰品",
            r".*选择后.+获得.+饰品",
            r".*进行后.+获得.+饰品",
        ]

        cfg.img_event.wait(timeout=5)
        while text_exists(cfg.img_src, r'SKIP.*') or text_exists(cfg.img_src, r"\d{2}:\d{2}:\d{2}:\d{2}"):
            cfg.img_event.clear()

            cfg.bboxes_event.wait(timeout=5)
            if (labels_exists(cfg.bboxes, Labels_ID['Skip']) or text_exists(cfg.img_src,
                                                                            r'SKIP.*')) and not labels_exists(
                cfg.bboxes, Labels_ID['Continue']):
                check_text_and_clickR(r'SKIP.*', clicks=10)
                check_label_and_clickR(cfg.bboxes, 'Skip')
                cfg.bboxes_event.clear()

            while attempts < max_attempts and any(text_exists(cfg.img_src, cond) for cond in event_text_conditions):
                for text_condition in event_text_conditions:
                    cfg.img_event.wait(timeout=20)

                    if text_exists(cfg.img_src, text_condition):
                        cfg.img_event.clear()
                        check_text_and_click(text_condition)
                        attempts = max_attempts
                        break

                attempts += 1

            if attempts >= max_attempts:
                logger.warning("未能匹配到预期选项文本，退出循环")

            cfg.img_event.wait(timeout=5)
            cfg.bboxes_event.wait(timeout=5)
            if text_exists(cfg.img_src, "继续") or labels_exists(cfg.bboxes, Labels_ID['Continue']):
                check_label_and_click(cfg.bboxes, 'Continue')
                cfg.img_event.clear()
                cfg.bboxes_event.clear()

            cfg.img_event.wait(timeout=5)
            cfg.bboxes_event.wait(timeout=5)
            if text_exists(cfg.img_src, r"选择一位罪人来进行判定.*") and text_exists(cfg.img_src, "极高"):
                check_label_and_click(cfg.bboxes, 'Advantage-High')
                check_text_and_clickR("极高")
                cfg.img_event.clear()
                cfg.bboxes_event.clear()
            elif text_exists(cfg.img_src, r"选择一位罪人来进行判定.*") and text_exists(cfg.img_src, "高"):
                check_text_and_clickR("高")
                cfg.img_event.clear()
                cfg.bboxes_event.clear()

            cfg.img_event.wait(timeout=5)
            if text_exists(cfg.img_src, "判定成功") and not text_exists(cfg.img_src, r"选择一位罪人来进行判定.*"):
                check_label_and_clickR(cfg.bboxes, 'Skip')
                mouse_click(900, 510, 5, 1, 'left')
                check_text_and_clickR(r'SKIP.*')
                cfg.img_event.clear()

            cfg.bboxes_event.wait(timeout=5)
            if labels_exists(cfg.bboxes, Labels_ID['Start']):
                check_label_and_click(cfg.bboxes, 'Start')
                cfg.bboxes_event.clear()

            cfg.bboxes_event.wait(timeout=5)
            if labels_exists(cfg.bboxes, Labels_ID['Continue']) and text_exists(cfg.img_src, "判定成功"):
                check_text_and_clickR("判定成功")
                check_label_and_click(cfg.bboxes, 'Continue')
                cfg.bboxes_event.clear()

        logger.info("结束异想体遭遇事件流程")

    def check_mirror_completion(self) -> bool:
        """检查镜牢4是否完成"""
        logger.trace("检查镜牢4是否完成")
        cfg.img_event.wait(timeout=5)
        while text_exists(cfg.img_src, '战斗胜利') or text_exists(cfg.img_src, '累计造成伤害') or text_exists(
                cfg.img_src, '探索完成') or text_exists(cfg.img_src, '总进度'):
            cfg.img_event.clear()

            cfg.bboxes_event.wait(timeout=5)
            check_label_and_click(cfg.bboxes, 'Confirm')
            cfg.bboxes_event.clear()

            cfg.img_event.wait(timeout=5)
            cfg.bboxes_event.wait(timeout=5)
            if text_exists(cfg.img_src, '探索完成') and text_exists(cfg.img_src, '总进度'):
                logger.info("镜牢4已完成")
                check_label_and_click(cfg.bboxes, 'Confirm')
                cfg.img_event.clear()
                cfg.bboxes_event.clear()

            cfg.img_event.wait(timeout=5)
            cfg.bboxes_event.wait(timeout=5)
            if text_exists(cfg.img_src, '探索结束奖励') and text_exists(cfg.img_src, '战斗通行证经验值'):
                logger.info("领取镜牢4探索奖励")
                check_text_and_click('领取')
                cfg.img_event.clear()
                cfg.bboxes_event.clear()

            cfg.img_event.wait(timeout=5)
            cfg.bboxes_event.wait(timeout=5)
            if text_exists(cfg.img_src, '通行证等级提升') and text_exists(cfg.img_src, '通行证等级'):
                check_text_and_click('确认')
                cfg.img_event.clear()
                cfg.bboxes_event.clear()

            return True

        return False

    def run(self):
        """循环执行镜牢4流程"""
        logger.info(f"开始执行镜牢4流程，循环次数为 {self.loop_count}")
        for _ in range(self.loop_count):
            if not self.mirror_switch:
                break
            try:
                self.mirror_pass_flag = False
                self.start_mirror_wuthering()
                self.current_count += 1
                logger.info(f"已完成第 {self.current_count} 次镜牢4")
                logger.info(f"即将进入第 {self.current_count + 1} 次镜牢4")
            except Exception as e:
                logger.error(f"镜牢4流程出错: {e}")
                logger.info("尝试回到主界面...")
                self.return_to_main_menu()

    def return_to_main_menu(self):
        """尝试回到主界面"""
        logger.info("尝试回到主界面...")
        for _ in range(10):
            if labels_exists(cfg.bboxes, Labels_ID['Settings']):
                check_label_and_click(cfg.bboxes, "Back")
                if text_exists(cfg.img_src, r"要保存并回到主菜单吗.*"):
                    check_label_and_click(cfg.bboxes, "Confirm")
                    logger.info("已退出镜像迷宫探索")
                return
            elif labels_exists(cfg.bboxes, Labels_ID['Back']):
                check_label_and_click(cfg.bboxes, "Back")
            else:
                check_label_and_click(cfg.bboxes, "Settings")
        logger.warning("无法回到主界面")

    def server_error(self):
        """服务器错误"""
        logger.warning("服务器发生错误,正在尝试重启....")

        cfg.img_event.wait(timeout=10)
        if text_exists(cfg.img_src, r'服务器发生错误.*'):
            mouse_click(1100, 745, 2, 1, 'left')
            check_text_and_clickR('重试')
            check_text_and_click('重试')
            cfg.img_event.clear()