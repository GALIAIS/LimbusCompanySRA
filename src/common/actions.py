import time
from pathlib import Path

from src.common.utils import *
from src.app.utils.ConfigManager import cfgm
from src.script.Luxcavation import luxcavation


def navigate_to_luxcavation():
    logger.info("判断是否处于驾驶席界面...")
    while True:
        cfg.bboxes_event.wait(timeout=5)
        if labels_exists(cfg.bboxes, Labels_ID['Drive']) and not labels_exists(cfg.bboxes, Labels_ID['Luxcavation']):
            check_label_and_click(cfg.bboxes, 'Drive')
            cfg.bboxes_event.clear()
            logger.info("已切换到驾驶席界面")
            continue
        cfg.bboxes_event.clear()

        cfg.bboxes_event.wait(timeout=5)
        if labels_exists(cfg.bboxes, Labels_ID['Mirror Dungeon']) and labels_exists(cfg.bboxes,
                                                                                    Labels_ID['Luxcavation']):
            check_label_and_click(cfg.bboxes, 'Luxcavation')
            cfg.bboxes_event.clear()
            logger.info("已切换到采光界面")
            continue
        cfg.bboxes_event.clear()

        cfg.bboxes_event.wait(timeout=5)
        if labels_exists(cfg.bboxes, Labels_ID['EXP']) and labels_exists(cfg.bboxes, Labels_ID['Thread']):
            cfg.bboxes_event.clear()
            break


def navigate_to_mirror_dungeons():
    """导航到镜像迷宫界面"""
    logger.info("判断是否处于驾驶席界面...")

    while True:
        if not (cfg.img_event.is_set() and cfg.bboxes_event.is_set()):
            cfg.img_event.wait(timeout=5)
            cfg.bboxes_event.wait(timeout=5)

        if labels_exists(cfg.bboxes, Labels_ID['Drive']) and not text_exists(cfg.img_src, '镜像迷宫'):
            logger.info("切换到驾驶席界面...")
            check_label_and_click(cfg.bboxes, 'Drive')
            cfg.img_event.clear()
            cfg.bboxes_event.clear()
            continue

        if labels_exists(cfg.bboxes, Labels_ID['Mirror Dungeon']) and labels_exists(cfg.bboxes,
                                                                                    Labels_ID['Luxcavation']):
            logger.info("尝试进入镜像迷宫...")
            check_label_and_click(cfg.bboxes, 'Mirror Dungeon')
            cfg.img_event.clear()
            cfg.bboxes_event.clear()
            continue

        if any(text_exists(cfg.img_src, text) for text in [r'呼啸之镜', r'梦中之镜']):
            logger.info("已进入镜像迷宫")
            cfg.img_event.clear()
            cfg.bboxes_event.clear()
            break

        cfg.img_event.clear()
        cfg.bboxes_event.clear()


def enter_mirror_dungeons():
    """进入镜像迷宫关卡"""
    while True:
        cfg.img_event.wait(timeout=5)
        cfg.bboxes_event.wait(timeout=5)

        if cfgm.get("Mirror_Dungeons.mirror_dungeons_choose") and text_exists(cfg.img_src,
                                                                              '每周加成') and not text_exists(
            cfg.img_src, '迷宫进度') and text_exists(
            cfg.img_src, '探索状态'):
            match cfgm.get("Mirror_Dungeons.mirror_dungeons_choose.selected"):
                case 1:
                    if text_exists(cfg.img_src, r'梦中之镜'):
                        check_text_and_clickR('进入')
                        cfg.img_event.clear()
                        cfg.bboxes_event.clear()
                        continue
                case 2:
                    if text_exists(cfg.img_src, 'SIMULATION'):
                        check_text_and_clickR('SIMULATION')
                        cfg.img_event.clear()
                        cfg.bboxes_event.clear()
                        continue
                case _:
                    logger.warning("未知镜像迷宫选择，跳过当前循环")
                    break

        if text_exists(cfg.img_src, '迷宫进度'):
            check_label_and_click(cfg.bboxes, 'Resume')
            logger.info("已恢复迷宫进度")
            cfg.img_event.clear()
            cfg.bboxes_event.clear()
            continue

        if text_exists(cfg.img_src, r'是否进入.*'):
            check_label_and_click(cfg.bboxes, 'Confirm')
            cfg.img_event.clear()
            cfg.bboxes_event.clear()
            continue

        if text_exists(cfg.img_src, '当前进度已过期。请领取您的奖励。'):
            check_label_and_click(cfg.bboxes, 'Confirm')
            logger.info("确认领取过期奖励")
            cfg.img_event.clear()
            cfg.bboxes_event.clear()
            continue

        if text_exists(cfg.img_src, '探索结束奖励') and not text_exists(cfg.img_src, '8/8'):
            check_label_and_click(cfg.bboxes, 'Give Up')
            logger.info("放弃奖励")
            cfg.img_event.clear()
            cfg.bboxes_event.clear()
            continue

        if text_exists(cfg.img_src, r'要在不领取奖励的情况下结束探索吗.*'):
            check_label_and_click(cfg.bboxes, 'Confirm')
            logger.info("确认放弃奖励")
            cfg.img_event.clear()
            cfg.bboxes_event.clear()
            continue

        if text_exists(cfg.img_src, '探索结束奖励') and text_exists(cfg.img_src, '8/8'):
            check_label_and_click(cfg.bboxes, 'Confirm')
            logger.info("已领取探索奖励")
            cfg.img_event.clear()
            cfg.bboxes_event.clear()
            continue

        if (not text_exists(cfg.img_src, '主题卡包图鉴') or not text_exists(cfg.img_src, '进入')) and not text_exists(
                cfg.img_src, '每周加成'):
            cfg.img_event.clear()
            cfg.bboxes_event.clear()
            break

        cfg.img_event.clear()
        cfg.bboxes_event.clear()

    logger.info("结束镜像迷宫流程")


def choose_initial_ego_gift():
    """选择初始E.G.O饰品"""
    ego_gift_choose = cfgm.get("Mirror_Dungeons.ego_gift_choose")[
        str(cfgm.get("Mirror_Dungeons.ego_gift_choose.selected"))]
    ego_gift_list = cfgm.get("Mirror_Dungeons.ego_gift_list")[ego_gift_choose]
    found_ego_gift = False
    while True:
        cfg.img_event.wait(timeout=5)
        cfg.bboxes_event.wait(timeout=5)
        if text_list_exists(cfg.img_src, ['烧伤', '流血', '突刺', '打击']) and text_exists(cfg.img_src,
                                                                                           '0/1') and not found_ego_gift:
            check_text_and_clickR(ego_gift_choose)
        cfg.img_event.clear()
        cfg.bboxes_event.clear()

        cfg.img_event.wait(timeout=5)
        cfg.bboxes_event.wait(timeout=5)
        if text_exists(cfg.img_src, r'选择.+饰品'):
            if not found_ego_gift:
                for ego_gift in ego_gift_list:
                    if text_exists(cfg.img_src, ego_gift):
                        found_ego_gift = True
                        break
        cfg.img_event.clear()
        cfg.bboxes_event.clear()

        cfg.img_event.wait(timeout=5)
        cfg.bboxes_event.wait(timeout=5)
        if text_list_exists(cfg.img_src, ['0/1', '0/2', '1/2']) and found_ego_gift:
            for ego_gift in ego_gift_list:
                if text_exists(cfg.img_src, ego_gift):
                    check_text_and_clickR(ego_gift)
                    cfg.img_event.clear()
                    cfg.bboxes_event.clear()
                    break
        cfg.img_event.clear()
        cfg.bboxes_event.clear()

        cfg.img_event.wait(timeout=5)
        cfg.bboxes_event.wait(timeout=5)
        if text_list_exists(cfg.img_src, ['1/1', '2/2']) or found_ego_gift:
            check_text_and_clickR(r"\b选择\b", 3)
            check_text_and_clickR(r"确认")
        cfg.img_event.clear()
        cfg.bboxes_event.clear()

        cfg.img_event.wait(timeout=5)
        cfg.bboxes_event.wait(timeout=5)
        if not text_exists(cfg.img_src, 'E.G.O饰品信息') and not text_exists(cfg.img_src, r'选择.+饰品'):
            logger.info("结束 E.G.O饰品选择流程")
            cfg.img_event.clear()
            cfg.bboxes_event.clear()
            break
        cfg.img_event.clear()
        cfg.bboxes_event.clear()

    logger.info("结束初始E.G.O饰品界面检测")


def ego_gift_event():
    """选择E.G.O饰品"""
    while True:
        cfg.img_event.wait(timeout=5)
        cfg.bboxes_event.wait(timeout=5)
        if (text_exists(cfg.img_src, r'选择.+饰品') or text_exists(cfg.img_src, r'获得.+饰品.*')) and text_exists(
                cfg.img_src, '0/1'):
            if text_exists(cfg.img_src, '敌方等级增加') and text_exists(cfg.img_src, '0/1'):
                check_text_and_clickR('敌方等级增加')
            elif labels_exists(cfg.bboxes, Labels_ID['E.G.O Gift']) and text_exists(cfg.img_src, '0/1'):
                check_label_and_click(cfg.bboxes, 'E.G.O Gift')
            cfg.img_event.clear()
            cfg.bboxes_event.clear()
            continue

        if text_list_exists(cfg.img_src, [r'选择.+饰品', r'获得.+饰品.*']) and not (text_exists(
                cfg.img_src, '0/1') or text_exists(cfg.img_src, 'E.G.O饰品信息')):
            if not text_exists(cfg.img_src, '1/1'):
                check_text_and_clickR(r'获得.+饰品.*')
                check_text_and_clickR('选择', 5)
                check_text_and_clickR('确认')
                cfg.img_event.clear()
                cfg.bboxes_event.clear()
                continue

        if text_exists(cfg.img_src, '1/1'):
            check_text_and_clickR('选择', 5)
            cfg.img_event.clear()
            cfg.bboxes_event.clear()
            continue

        cfg.img_event.wait(timeout=5)
        cfg.bboxes_event.wait(timeout=5)
        if (labels_exists(cfg.bboxes, Labels_ID['Confirm']) or text_exists(cfg.img_src, r'确认')) and text_exists(
                cfg.img_src, r'获得.+饰品.*'):
            if text_exists(cfg.img_src, r'确认'):
                check_text_and_clickR('确认')
            else:
                check_label_and_click(cfg.bboxes, 'Confirm')
            cfg.img_event.clear()
            cfg.bboxes_event.clear()
            continue

        if not text_exists(cfg.img_src, r'选择.+饰品') and not text_exists(cfg.img_src,
                                                                           r'获得.+饰品.*') and not text_exists(
            cfg.img_src, 'E.G.O饰品信息'):
            cfg.img_event.clear()
            cfg.bboxes_event.clear()
            break
        cfg.img_event.clear()
        cfg.bboxes_event.clear()

    logger.info("结束E.G.O饰品界面检测")


def choose_encounter_reward_card():
    """选择遭遇战奖励卡"""
    while True:
        cfg.img_event.wait(timeout=5)
        cfg.bboxes_event.wait(timeout=5)
        if text_exists(cfg.img_src, '选择遭遇战奖励卡') and not text_exists(cfg.img_src, r'1/1'):
            if text_exists(cfg.img_src, r'获得.+经费'):
                check_text_and_clickR(r'获得.+经费')
            elif text_exists(cfg.img_src, r'获得.+经费') and text_exists(cfg.img_src, r'概率获得'):
                check_text_and_clickR(r'概率获得')
            elif text_exists(cfg.img_src, r'\b获得一件'):
                check_text_and_clickR(r'\b获得一件')
            elif text_exists(cfg.img_src, r'随机.+罪孽碎片.*'):
                check_text_and_clickR(r'随机.+罪孽碎片.*')
            else:
                check_label_and_click(cfg.bboxes, 'Encounter Reward Card')
            cfg.img_event.clear()
            cfg.bboxes_event.clear()
            continue
        cfg.img_event.clear()
        cfg.bboxes_event.clear()

        if text_exists(cfg.img_src, r'1/1') and text_exists(cfg.img_src, '选择遭遇战奖励卡'):
            if text_exists(cfg.img_src, r'确认'):
                check_text_and_clickR('确认')
            else:
                check_label_and_click(cfg.bboxes, 'Confirm')
            cfg.img_event.clear()
            cfg.bboxes_event.clear()
            continue
        cfg.img_event.clear()
        cfg.bboxes_event.clear()

        if text_exists(cfg.img_src, r'获得E.G.O饰品.*') and text_exists(cfg.img_src, r'确认'):
            check_text_and_clickR('确认')
            cfg.img_event.clear()
            cfg.bboxes_event.clear()
            continue
        cfg.img_event.clear()
        cfg.bboxes_event.clear()

        if not text_exists(cfg.img_src, '选择遭遇战奖励卡') and not text_exists(cfg.img_src, '遭遇战奖励卡指南'):
            cfg.img_event.clear()
            cfg.bboxes_event.clear()
            break
        cfg.img_event.clear()
        cfg.bboxes_event.clear()

    logger.info("结束选择遭遇战奖励卡界面检测")


# def confirm_ego_gift_info():
#     """确认E.G.O饰品信息"""
#     while True:
#         cfg.img_event.wait(timeout=5)
#         cfg.bboxes_event.wait(timeout=5)
#         if text_exists(cfg.img_src, 'E.G.O饰品信息') or text_exists(cfg.img_src, r'获得E.G.O饰品.*'):
#             check_text_in_model_and_click(r'选择.+饰品')
#             cfg.img_event.clear()
#             cfg.bboxes_event.clear()
#             continue
#         cfg.img_event.clear()
#         cfg.bboxes_event.clear()
#
#         if labels_exists(cfg.bboxes, Labels_ID['Confirm']) or text_exists(cfg.img_src, r'确认'):
#             if text_exists(cfg.img_src, r'确认'):
#                 check_text_and_clickR('确认')
#             else:
#                 check_label_and_click(cfg.bboxes, 'Confirm')
#             cfg.img_event.clear()
#             cfg.bboxes_event.clear()
#             continue
#         cfg.img_event.clear()
#         cfg.bboxes_event.clear()
#
#         if not text_exists(cfg.img_src, 'E.G.O饰品信息') or not text_exists(cfg.img_src, r'获得.+饰品.*'):
#             cfg.img_event.clear()
#             cfg.bboxes_event.clear()
#             break
#     logger.info("结束E.G.O饰品信息界面检测")
def confirm_ego_gift_info():
    """确认E.G.O饰品信息"""
    logger.info("开始E.G.O饰品信息界面检测")
    while True:
        cfg.img_event.wait(timeout=5)
        if not cfg.img_event.is_set():
            continue

        ocr_result = ocrx_process(get_ocrx_data(cfg.img_src))
        bboxes = cfg.bboxes

        if any(res['text'] == 'E.G.O饰品信息' for res in ocr_result) or any(
                res['text'].startswith('获得E.G.O饰品') for res in ocr_result):
            click_center_of_textR(next(
                (res['coordinates'] for res in ocr_result if res['text'].startswith('选择') and '饰品' in res['text']),
                None))
            cfg.img_event.clear()
            continue

        if labels_exists(bboxes, Labels_ID['Confirm']) or any(res['text'] == '确认' for res in ocr_result):
            if any(res['text'] == '确认' for res in ocr_result):
                click_center_of_textR(next((res['coordinates'] for res in ocr_result if res['text'] == '确认'), None))
            else:
                check_label_and_click(bboxes, 'Confirm')
            cfg.img_event.clear()
            continue

        if not any(res['text'] == 'E.G.O饰品信息' for res in ocr_result) or not any(
                res['text'].startswith('获得') and '饰品' in res['text'] for res in ocr_result):
            cfg.img_event.clear()
            break

    logger.info("结束E.G.O饰品信息界面检测")


def team_formation():
    """编队"""
    logger.info("进入初始编队界面")

    try:
        while True:
            cfg.img_event.wait(timeout=5)
            cfg.bboxes_event.wait(timeout=5)
            if text_exists(cfg.img_src, r'编队.*') and text_exists(cfg.img_src, '罪孽碎片'):
                time.sleep(3)
                check_text_and_clickR(r'确认')
                cfg.img_event.clear()
                cfg.bboxes_event.clear()
                continue
            cfg.img_event.clear()
            cfg.bboxes_event.clear()
            if not text_exists(cfg.img_src, '播报员') and not text_exists(cfg.img_src, '确认') and not text_exists(
                    cfg.img_src, '罪孽碎片'):
                break
    except Exception as e:
        logger.error(f"编队操作发生异常: {e}")
    logger.info("结束初始编队界面检测")


def choose_grace_of_the_dreaming_star():
    grace_of_the_dreaming_stars = cfgm.get("Mirror_Dungeons.grace_of_the_dreaming_star_choose")
    choose_any_option = False

    if not grace_of_the_dreaming_stars:
        logger.info("grace_of_the_dreaming_stars 列表为空，自动选择 '起始之星'")
        cfg.img_event.wait(timeout=5)
        check_text_and_clickR('起始之星')
        cfg.img_event.clear()
        logger.info("结束星之恩惠界面检测")
        return

    while True:
        if not choose_any_option:
            for grace_of_the_dreaming_star in grace_of_the_dreaming_stars:
                cfg.img_event.wait(timeout=5)
                if text_exists(cfg.img_src, grace_of_the_dreaming_star):
                    check_text_and_clickR(grace_of_the_dreaming_star)
                    cfg.img_event.clear()
            choose_any_option = True

        cfg.img_event.wait(timeout=5)
        if not text_list_exists(cfg.img_src, [r'选择星之恩惠', r'要选择此效果吗.*'], match_mode='all'):
            check_text_and_clickR(r'完成')
            check_text_and_clickR(r'确认')
        cfg.img_event.clear()

        cfg.img_event.wait(timeout=5)
        if text_list_exists(cfg.img_src, [r'选择星之恩惠', r'要选择此效果吗.*']):
            check_text_and_clickR(r'确认')
        cfg.img_event.clear()

        cfg.img_event.wait(timeout=5)
        if not text_exists(cfg.img_src, r'梦中的星之恩惠') and choose_any_option:
            cfg.img_event.clear()
            break
        cfg.img_event.clear()

    logger.info("结束星之恩惠界面检测")


def choose_themes_pack():
    """选择主题卡包"""
    theme_packs = cfgm.get("Mirror_Dungeons.theme_pack_choose")
    while True:
        for theme_pack in theme_packs:
            if not cfg.img_event.wait(timeout=5):
                logger.warning("img_event 等待超时")
                continue
            if not cfg.bboxes_event.wait(timeout=5):
                logger.warning("bboxes_event 等待超时")
                continue

            if text_exists(cfg.img_src, theme_pack):
                if labels_exists(cfg.bboxes, Labels_ID['Themes Pack']):
                    # check_label_text_and_drag(theme_pack, cfg.bboxes, 'Themes Pack')
                    locate_and_drag(cfg.img_src, theme_pack)
                else:
                    logger.warning("未发现标签，可能需要处理其他逻辑")
                cfg.img_event.clear()
                cfg.bboxes_event.clear()
                break
        else:
            if not cfg.img_event.wait(timeout=5):
                logger.warning("img_event 等待超时")
                continue
            if not cfg.bboxes_event.wait(timeout=5):
                logger.warning("bboxes_event 等待超时")
                continue

            check_label_and_drag(cfg.bboxes, 'Themes Pack')
            cfg.img_event.clear()
            cfg.bboxes_event.clear()

        if not text_exists(cfg.img_src, r'选择.+层主题卡包'):
            break

    logger.info("结束Themes Pack界面检测")


def choose_path():
    """选择路径"""
    logger.info("开始选择路径...")

    NODE_PRIORITY = {
        Labels_ID.get('Safe Node', None): 4.0,
        Labels_ID.get('Event Node', None): 3.0,
        Labels_ID.get('Battle Node', None): 2.0,
        Labels_ID.get('Current Node', None): 1.0,
        Labels_ID.get('End Node', None): 0.0
    }

    node_attempts = {}
    cfg.img_event.wait(timeout=5)
    cfg.bboxes_event.wait(timeout=5)

    while text_exists(cfg.img_src, r'正在探索第.+层') and not labels_exists(cfg.bboxes, Labels_ID['Enter']):
        cfg.img_event.clear()
        cfg.bboxes_event.clear()
        mouse_scroll(-200)

        cfg.bboxes_event.wait(timeout=5)
        bboxes = cfg.bboxes
        cfg.bboxes_event.clear()

        available_nodes = sorted(
            [
                (bbox, NODE_PRIORITY[label_id])
                for bbox in bboxes
                for label_id in NODE_PRIORITY
                if label_id is not None and label_exists(bbox, label_id)
            ],
            key=lambda x: (-x[1], x[0][0])
        )

        if not available_nodes:
            logger.warning("未找到可点击的节点，尝试重新检测...")
            mouse_scroll(-200)
            cfg.bboxes_event.wait(timeout=5)
            bboxes = cfg.bboxes
            available_nodes = sorted(
                [
                    (bbox, NODE_PRIORITY[label_id])
                    for bbox in bboxes
                    for label_id in NODE_PRIORITY
                    if label_id is not None and label_exists(bbox, label_id)
                ],
                key=lambda x: (-x[1], x[0][0])
            )
            if not available_nodes:
                logger.error("多次尝试后仍未检测到可用节点，终止选择路径")
                break

        available_nodes = [
            node for node in available_nodes
            if node_attempts.get(node[0][5], 0) < (2 if node[1] >= 3.0 else 1)
        ]

        if not available_nodes:
            logger.warning("所有节点已尝试上限，无法继续选择")
            break

        selected_node = available_nodes[0]
        node_id = selected_node[0][5] if len(selected_node[0]) > 5 else None

        if node_id is None:
            logger.error("节点数据结构不符合预期，无法获取 node_id")
            break

        node_attempts[node_id] = node_attempts.get(node_id, 0) + 1

        cfg.bboxes_event.wait(timeout=5)
        check_label_id_and_click(cfg.bboxes, node_id)
        cfg.bboxes_event.clear()

        cfg.img_event.wait(timeout=5)
        cfg.bboxes_event.wait(timeout=5)
        if text_exists(cfg.img_src, '进入') or labels_exists(cfg.bboxes, Labels_ID['Enter']):
            check_label_and_click(cfg.bboxes, 'Enter')
            cfg.img_event.clear()
            cfg.bboxes_event.clear()
            break

    logger.info("结束路径选择")


def shop_buy(max_heal_count: int = 1):
    heal_count = 0
    if text_exists(cfg.img_src, '治疗罪人') and heal_count < max_heal_count and not text_list_exists(cfg.img_src,
                                                                                                     [
                                                                                                         r'可以恢复或是复活罪人.*',
                                                                                                         '结果'],
                                                                                                     match_mode='all'):
        check_text_and_clickR('治疗罪人')
        heal_count += 1

    while True:
        cfg.img_event.wait(timeout=5)
        cfg.bboxes_event.wait(timeout=5)

        if any(text_exists(cfg.img_src, pattern) for pattern in [
            r'.*让全体罪人坐在椅子上休息.*',
            r"全体罪人恢复.+体力.+理智值",
            '选择能量饮料',
            '购买成功'
        ]) and not text_exists(cfg.img_src, '结果'):
            check_text_and_clickR(r'全体罪人恢复.+体力.+理智值')
            continue

        if text_exists(cfg.img_src, '选择看上去疲倦的罪人') or text_exists(cfg.img_src, r'让谁休息比较好呢.*'):
            check_text_and_clickR(r'选择看上去疲倦的罪人')
            continue

        if text_exists(cfg.img_src, r'全体罪人的体力与理智值恢复了.*'):
            check_text_and_clickR('返回')
            continue

        if text_list_exists(cfg.img_src, ['售卖饰品', '编队']) and not heal_count < max_heal_count:
            check_label_and_click(cfg.bboxes, 'Leava')
            continue

        if any(text_exists(cfg.img_src, pattern) for pattern in [
            r'要离开休息点吗.*',
            r'要离开商店吗.*'
        ]):
            check_label_and_click(cfg.bboxes, 'Confirm')
            continue

        if not any(text_exists(cfg.img_src, text) for text in ['商店', '治疗罪人', '编队', '离开']):
            cfg.img_event.clear()
            cfg.bboxes_event.clear()
            break

    logger.info("结束商店购买界面检测")


def enter_event():
    """进入事件界面"""
    while True:
        cfg.img_event.wait(timeout=5)
        cfg.bboxes_event.wait(timeout=5)
        if text_exists(cfg.img_src, '进入'):
            check_label_and_click(cfg.bboxes, 'Enter')
            cfg.img_event.clear()
            cfg.bboxes_event.clear()
            continue
        cfg.img_event.clear()
        cfg.bboxes_event.clear()
        if not text_exists(cfg.img_src, '通关奖励') or not text_exists(cfg.img_src, '进入'):
            cfg.img_event.clear()
            cfg.bboxes_event.clear()
            break
        cfg.img_event.clear()
        cfg.bboxes_event.clear()

    logger.info("结束进入事件界面检测")


def battle_choose_characters():
    """参战角色选择"""
    logger.info("参战角色选择界面")
    while True:
        cfg.img_event.wait(timeout=5)
        cfg.bboxes_event.wait(timeout=5)
        if not text_exists(cfg.img_src, r'\b12/12\b') and text_exists(cfg.img_src, '开始战斗'):
            # check_label_and_click(cfg.bboxes, 'Start')
            cfg.img_event.clear()
            cfg.bboxes_event.clear()
            continue
        elif text_exists(cfg.img_src, r'\b12/12\b') and text_exists(cfg.img_src, '开始战斗'):
            # check_label_and_click(cfg.bboxes, 'Start')
            check_text_and_clickR('开始战斗')
            cfg.img_event.clear()
            cfg.bboxes_event.clear()

        cfg.img_event.wait(timeout=5)
        cfg.bboxes_event.wait(timeout=5)
        if not text_exists(cfg.img_src, r'\b12/12\b') and not text_exists(cfg.img_src, '开始战斗'):
            cfg.img_event.clear()
            cfg.bboxes_event.clear()
            break
        cfg.img_event.clear()
        cfg.bboxes_event.clear()

    logger.info("结束参战角色选择界面检测")


def start_battle():
    """战斗事件流程"""
    win_rate_clicked = False

    while True:
        cfg.img_event.wait(timeout=5)
        cfg.bboxes_event.wait(timeout=5)
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

        cfg.img_event.wait(timeout=5)
        cfg.bboxes_event.wait(timeout=5)
        if (text_exists(cfg.img_src, '胜率') or labels_exists(cfg.bboxes,
                                                              Labels_ID['Win Rate'])) and not win_rate_clicked:
            check_label_and_clickR(cfg.bboxes, 'Win Rate')
            cfg.img_event.clear()
            cfg.bboxes_event.clear()
            win_rate_clicked = True
            time.sleep(2)

        cfg.img_event.wait(timeout=5)
        cfg.bboxes_event.wait(timeout=5)
        if text_exists(cfg.img_src, r'.*TART') or labels_exists(cfg.bboxes, Labels_ID['Start']):
            check_label_and_clickR(cfg.bboxes, 'Start')
            cfg.img_event.clear()
            cfg.bboxes_event.clear()
            win_rate_clicked = False
            time.sleep(5)

            cfg.img_event.wait(timeout=5)
            if not (text_exists(cfg.img_src, r'胜率.*') or text_exists(cfg.img_src, r'伤害.*')):
                cfg.img_event.clear()
                continue

        cfg.img_event.wait(timeout=5)
        if text_exists(cfg.img_src, r'SKIP.*') or text_exists(cfg.img_src, r"\d{2}:\d{2}:\d{2}:\d{2}"):
            logger.info("检测到异想体遭遇事件")
            cfg.img_event.clear()
            abnormality_encounters_event()
        cfg.img_event.clear()

        cfg.img_event.wait(timeout=5)
        cfg.bboxes_event.wait(timeout=5)
        if not labels_exists(cfg.bboxes, Labels_ID['Win Rate']) and not labels_exists(cfg.bboxes,
                                                                                      Labels_ID['Damage']) and (
                text_exists(cfg.img_src, '选择遭遇战奖励卡')
                or text_exists(cfg.img_src, '遭遇战奖励卡指南')
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


def abnormality_encounters_event():
    """异想体遭遇事件流程"""
    event_text_conditions = [
        r".*成功后.+获得.+饰品",
        r".*选择后.+获得.+饰品",
        r".*进行后.+获得.+饰品",
        r"根据后续选项.+获得.+饰品",
        r"调查工厂",
        r"不是",
        r"拒绝"
    ]

    try:
        while True:
            cfg.img_event.wait(timeout=5)
            cfg.bboxes_event.wait(timeout=5)

            if (text_exists(cfg.img_src, "SKIP") or
                    labels_exists(cfg.bboxes, Labels_ID['Skip']) or
                    text_exists(cfg.img_src, r"\d{2}:\d{2}:\d{2}:\d{2}") or
                    any(text_exists(cfg.img_src, cond) for cond in event_text_conditions) or
                    text_exists(cfg.img_src, "继续") or
                    labels_exists(cfg.bboxes, Labels_ID['Continue']) or
                    labels_exists(cfg.bboxes, Labels_ID['Leava']) or
                    text_exists(cfg.img_src, r"选择一位罪人来进行判定.*") or
                    (text_exists(cfg.img_src, r"预计成功率.*") and labels_exists(cfg.bboxes, Labels_ID['Start'])) or
                    ((text_exists(cfg.img_src, "判定成功") or text_exists(cfg.img_src, "判定失败")) and not text_exists(
                        cfg.img_src, r"选择一位罪人来进行判定.*"))):

                if (labels_exists(cfg.bboxes, Labels_ID['Skip']) or text_exists(cfg.img_src,
                                                                                "SKIP")) and not (text_exists(
                    cfg.img_src, r"该如何快择") or text_exists(cfg.img_src, r"选择一位罪人来进行判定.*")):
                    if text_exists(cfg.img_src, "SKIP"):
                        check_text_and_clickR(r'SKIP', 10)
                    else:
                        mouse_click(900, 515, 10)
                cfg.img_event.clear()
                cfg.bboxes_event.clear()

                cfg.img_event.wait(timeout=5)
                cfg.bboxes_event.wait(timeout=5)
                if any(text_exists(cfg.img_src, cond) for cond in event_text_conditions):
                    for text_condition in event_text_conditions:
                        if text_exists(cfg.img_src, text_condition):
                            check_text_and_clickR(text_condition)
                            break
                cfg.img_event.clear()
                cfg.bboxes_event.clear()

                cfg.img_event.wait(timeout=5)
                cfg.bboxes_event.wait(timeout=5)
                if text_exists(cfg.img_src, "继续") or labels_exists(cfg.bboxes,
                                                                     Labels_ID['Continue']) or labels_exists(
                    cfg.bboxes, Labels_ID['Leava']):
                    check_text_and_clickR("继续")
                    check_label_and_click(cfg.bboxes, 'Continue')
                    check_label_and_click(cfg.bboxes, 'Leava')
                cfg.img_event.clear()
                cfg.bboxes_event.clear()

                cfg.img_event.wait(timeout=5)
                cfg.bboxes_event.wait(timeout=5)
                if text_exists(cfg.img_src, r"选择一位罪人来进行判定.*"):
                    if text_exists(cfg.img_src, "极高"):
                        check_text_and_clickR("极高")
                    if labels_exists(cfg.bboxes, Labels_ID['Advantage-High']):
                        check_label_and_clickR(cfg.bboxes, 'Advantage-High')
                    if text_exists(cfg.img_src, "高"):
                        check_text_and_clickR(r"高")
                    if not text_list_exists(cfg.img_src, ["极高", "高"]) and not labels_exists(cfg.bboxes, Labels_ID[
                        'Advantage-High']):
                        mouse_click(122, 1035)
                cfg.img_event.clear()
                cfg.bboxes_event.clear()

                cfg.img_event.wait(timeout=5)
                cfg.bboxes_event.wait(timeout=5)
                if text_exists(cfg.img_src, r"预计成功率.*") and text_exists(cfg.img_src, '进行判定'):
                    if labels_exists(cfg.bboxes, Labels_ID['Start']):
                        check_label_and_click(cfg.bboxes, 'Start')
                    if text_exists(cfg.img_src, '进行判定'):
                        check_text_and_clickR('进行判定')
                cfg.img_event.clear()
                cfg.bboxes_event.clear()

                cfg.img_event.wait(timeout=5)
                cfg.bboxes_event.wait(timeout=5)
                if (text_exists(cfg.img_src, "判定成功") or text_exists(cfg.img_src, "判定失败")) and not text_exists(
                        cfg.img_src, r"选择一位罪人来进行判定.*"):
                    if text_exists(cfg.img_src, "SKIP"):
                        check_text_and_clickR(r'SKIP', 10)
                    else:
                        mouse_click(900, 515, 10)
                cfg.img_event.clear()
                cfg.bboxes_event.clear()

            cfg.img_event.wait(timeout=5)
            cfg.bboxes_event.wait(timeout=5)
            if not text_exists(cfg.img_src, 'SKIP') and not text_exists(cfg.img_src, r"\d{2}:\d{2}:\d{2}:\d{2}"):
                cfg.img_event.clear()
                break

            cfg.img_event.clear()
            cfg.bboxes_event.clear()

    except Exception as e:
        logger.error(f"异想体流程发生错误: {e}")
    finally:
        logger.info("结束异想体遭遇事件流程")


def check_mirror_completion() -> bool:
    """检查镜牢4是否完成"""
    cfg.img_event.wait(timeout=5)
    if not any(text_exists(cfg.img_src, pattern) for pattern in [
        '战斗胜利', '累计造成伤害', '探索完成', '总进度', '探索结束奖励']):
        cfg.img_event.clear()
        return False
    cfg.img_event.clear()

    while True:
        cfg.img_event.wait(timeout=5)
        cfg.bboxes_event.wait(timeout=5)
        if text_list_exists(cfg.img_src, ['战斗胜利', '累计造成伤害', '优秀员工']):
            check_label_and_click(cfg.bboxes, 'Confirm')
            cfg.img_event.clear()
            cfg.bboxes_event.clear()
            continue
        cfg.img_event.clear()
        cfg.bboxes_event.clear()

        cfg.img_event.wait(timeout=5)
        cfg.bboxes_event.wait(timeout=5)
        if text_exists(cfg.img_src, '探索完成') and text_exists(cfg.img_src, '总进度'):
            check_label_and_click(cfg.bboxes, 'Confirm')
            cfg.img_event.clear()
            cfg.bboxes_event.clear()
            continue
        cfg.img_event.clear()
        cfg.bboxes_event.clear()

        cfg.img_event.wait(timeout=5)
        cfg.bboxes_event.wait(timeout=5)
        if text_exists(cfg.img_src, r'要消耗.+领取额外奖励.*'):
            check_label_and_click(cfg.bboxes, 'Confirm')
            cfg.img_event.clear()
            cfg.bboxes_event.clear()
            continue
        cfg.img_event.clear()
        cfg.bboxes_event.clear()

        cfg.img_event.wait(timeout=5)
        cfg.bboxes_event.wait(timeout=5)
        if text_exists(cfg.img_src, '探索结束奖励') and text_exists(cfg.img_src, '战斗通行证经验值'):
            check_text_in_model_and_click('领取')
            cfg.img_event.clear()
            cfg.bboxes_event.clear()
            continue
        cfg.img_event.clear()
        cfg.bboxes_event.clear()

        cfg.img_event.wait(timeout=5)
        cfg.bboxes_event.wait(timeout=5)
        if text_exists(cfg.img_src, '通行证等级提升') and text_exists(cfg.img_src, '通行证等级'):
            check_label_and_click(cfg.bboxes, 'Confirm')
            cfg.img_event.clear()
            cfg.bboxes_event.clear()
            continue
        cfg.img_event.clear()
        cfg.bboxes_event.clear()

        cfg.img_event.wait(timeout=5)
        if not any(text_exists(cfg.img_src, pattern) for pattern in [
            '战斗胜利', '累计造成伤害', '探索完成', '总进度', '探索结束奖励']):
            logger.info("胜利检测结束")
            cfg.img_event.clear()
            return True
        cfg.img_event.clear()


def return_to_main_menu():
    """尝试回到主界面"""
    logger.info("尝试回到主界面...")
    for _ in range(10):
        if labels_exists(cfg.bboxes, Labels_ID['Settings']):
            check_label_and_click(cfg.bboxes, "Back")
            if text_exists(cfg.img_src, r"要保存并回到主菜单吗.*"):
                check_label_and_click(cfg.bboxes, "Confirm")
                logger.info("已退出镜像迷宫探索")
                break
            return
        elif labels_exists(cfg.bboxes, Labels_ID['Back']):
            check_label_and_click(cfg.bboxes, "Back")
        else:
            check_label_and_click(cfg.bboxes, "Settings")
    logger.warning("无法回到主界面")


def server_error():
    """服务器错误"""
    logger.warning("服务器发生错误,正在尝试重启....")

    time.sleep(8)
    cfg.img_event.wait(timeout=5)
    if text_exists(cfg.img_src, r'服务器发生错误.*'):
        mouse_click(1100, 745, 2, 1, 'left')
        # check_text_in_model_and_clickR('重试')
        check_text_in_model_and_click('重试')
        cfg.img_event.clear()


def other_event():
    cfg.img_event.wait(timeout=5)
    cfg.bboxes_event.wait(timeout=5)
    if text_exists(cfg.img_src, r'获得.+饰品.*'):
        check_label_and_click(cfg.bboxes, 'Confirm')
        cfg.img_event.clear()
        cfg.bboxes_event.clear()


def run():
    """执行自动化流程"""

    def execute_process(process_name, switch_key, loop_count_key, process_func):
        current_count = 1
        is_switch_on = cfgm.get(switch_key)
        max_loops = cfgm.get(loop_count_key)

        if not is_switch_on:
            logger.info(f"{process_name}流程未开启")
            return

        for _ in range(max_loops):
            try:
                logger.info(f"开始执行第 {current_count} 次{process_name}流程")
                process_func()
                logger.info(f"已完成第 {current_count} 次{process_name}流程")

                if current_count >= max_loops:
                    logger.trace(f"已完成所有 {process_name} 流程")
                else:
                    logger.info(f"即将进入第 {current_count + 1} 次{process_name}流程")

                current_count += 1
            except Exception as e:
                logger.error(f"{process_name}流程出错: {e}")
                logger.info("尝试回到主界面...")
                return_to_main_menu()
                break

    execute_process(
        process_name="镜像迷宫",
        switch_key="Mirror_Dungeons.mirror_switch",
        loop_count_key="Mirror_Dungeons.mirror_loop_count",
        process_func=lambda: __import__('src.script.Mirror_Dungeon').script.Mirror_Dungeon.mw.start_mirror_dungeon()
    )

    execute_process(
        process_name="EXP副本",
        switch_key="Luxcavation.exp_switch",
        loop_count_key="Luxcavation.luxcavation_loop_count",
        process_func=lambda: luxcavation.Luxcavation_EXP()
    )

    execute_process(
        process_name="Thread副本",
        switch_key="Luxcavation.thread_switch",
        loop_count_key="Luxcavation.luxcavation_loop_count",
        process_func=lambda: luxcavation.Luxcavation_Thread()
    )
