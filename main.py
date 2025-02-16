# script/GroupLink/main.py

import logging
import os
import sys
import re
import json
import asyncio
from datetime import datetime

# 添加项目根目录到sys.path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from app.config import *
from app.api import *
from app.switch import load_switch, save_switch


# 数据存储路径，实际开发时，请将GroupLink替换为具体的数据存放路径
DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data",
    "GroupLink",
)


# 查看功能开关状态
def load_function_status(group_id):
    return load_switch(group_id, "GroupLink")


# 保存功能开关状态
def save_function_status(group_id, status):
    save_switch(group_id, "GroupLink", status)


# 处理元事件，用于启动时确保数据目录存在
async def handle_GroupLink_meta_event(websocket):
    os.makedirs(DATA_DIR, exist_ok=True)


# 处理开关状态
async def toggle_function_status(websocket, group_id, message_id, authorized):
    if not authorized:
        await send_group_msg(
            websocket,
            group_id,
            f"[CQ:reply,id={message_id}]❌❌❌你没有权限对GroupLink功能进行操作,请联系管理员。",
        )
        return

    if load_function_status(group_id):
        save_function_status(group_id, False)
        await send_group_msg(
            websocket,
            group_id,
            f"[CQ:reply,id={message_id}]🚫🚫🚫GroupLink功能已关闭",
        )
    else:
        save_function_status(group_id, True)
        await send_group_msg(
            websocket, group_id, f"[CQ:reply,id={message_id}]✅✅✅GroupLink功能已开启"
        )


def load_group_link(category):
    """
    加载群互联
    """
    try:
        if not os.path.exists(os.path.join(DATA_DIR, f"group_link_data.json")):
            return []

        with open(
            os.path.join(DATA_DIR, f"group_link_data.json"), "r", encoding="utf-8"
        ) as f:
            group_link_data = json.load(f)

            return group_link_data.get(category, [])
    except Exception as e:
        logging.error(f"加载群互联失败: {e}")
        return []


def save_group_link(category, group_links):
    """
    保存群互联，保存某分类及其分类下的数组到JSON文件，保持其他分类数据不变
    """
    try:
        # 读取现有数据
        existing_data = {}
        if os.path.exists(os.path.join(DATA_DIR, f"group_link_data.json")):
            with open(
                os.path.join(DATA_DIR, f"group_link_data.json"), "r", encoding="utf-8"
            ) as f:
                existing_data = json.load(f)

        # 更新指定分类的数据
        existing_data[category] = group_links

        # 保存所有数据
        with open(
            os.path.join(DATA_DIR, f"group_link_data.json"), "w", encoding="utf-8"
        ) as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logging.error(f"保存群互联失败: {e}")
        return False


def load_group_link_category(group_id):
    """
    加载群互联分类，以数组返回
    """
    try:
        with open(
            os.path.join(DATA_DIR, f"group_link_data.json"), "r", encoding="utf-8"
        ) as f:
            group_link_data = json.load(f)
            group_link_category = []
            for category in group_link_data:
                if group_id in group_link_data[category]:
                    group_link_category.append(category)
            return group_link_category

    except Exception as e:
        logging.error(f"加载群互联分类失败: {e}")
        return None


async def add_group_link(websocket, group_id, message_id, raw_message, authorized):
    """
    添加群互联
    """
    try:
        if authorized:
            match = re.match("add互联(.*)", raw_message)
            if match:
                category = match.group(1)
                # 读取该分类下的数组
                group_links = load_group_link(category)
                # 检查群互联是否已存在
                if group_id in group_links:
                    await send_group_msg(
                        websocket,
                        group_id,
                        f"[CQ:reply,id={message_id}]❌❌❌本群已添加互联【{category}】,请勿重复添加",
                    )
                    return False
                # 添加数组元素
                group_links.append(group_id)
                # 保存群互联
                if save_group_link(category, group_links):
                    await send_group_msg(
                        websocket,
                        group_id,
                        f"[CQ:reply,id={message_id}]✅✅✅已添加群互联【{category}】",
                    )
                    return True
                else:
                    await send_group_msg(
                        websocket,
                        group_id,
                        f"[CQ:reply,id={message_id}]❌❌❌添加群互联失败",
                    )
                    return False

    except Exception as e:
        logging.error(f"添加群互联失败: {e}")
        return False


async def delete_group_link(websocket, group_id, message_id, raw_message, authorized):
    """
    删除群互联
    """
    try:
        if authorized:
            match = re.match("rm互联(.*)", raw_message)
            if match:
                category = match.group(1)
                group_links = load_group_link(category)

                # 检查群互联是否存在
                if group_id not in group_links:
                    await send_group_msg(
                        websocket,
                        group_id,
                        f"[CQ:reply,id={message_id}]❌❌❌本群未添加互联【{category}】",
                    )
                    return False

                # 删除群互联
                group_links.remove(group_id)
                if save_group_link(category, group_links):
                    await send_group_msg(
                        websocket,
                        group_id,
                        f"[CQ:reply,id={message_id}]✅✅✅已删除群互联【{category}】",
                    )
                    return True
                else:
                    await send_group_msg(
                        websocket,
                        group_id,
                        f"[CQ:reply,id={message_id}]❌❌❌删除群互联失败",
                    )
                    return False
    except Exception as e:
        logging.error(f"删除群互联失败: {e}")
        return False


async def send_group_link_message(websocket, user_id, group_id, raw_message):
    """
    把某群的消息转发到互联群
    """
    try:
        # 获取该群的互联群
        group_link_category = load_group_link_category(group_id)
        if group_link_category:
            for category in group_link_category:
                group_links = load_group_link(category)
                for link_group_id in group_links:
                    # 必须不是自己
                    if link_group_id != group_id:
                        # 目标群是否开启群互联
                        if load_function_status(link_group_id):
                            # 如果消息是JSON卡片，则不转发
                            if "CQ:json,data=" in raw_message:
                                return
                            # 如果消息是选课查询或平均分，则不转发
                            if raw_message.startswith(
                                "选课查询"
                            ) or raw_message.startswith("平均分"):
                                return
                            else:
                                message = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n群【{group_id}】的【{user_id}】说：\n\n{raw_message}"
                                await send_group_msg(websocket, link_group_id, message)

    except Exception as e:
        logging.error(f"发送群互联消息失败: {e}")
        return False


# 群消息处理函数
async def handle_GroupLink_group_message(websocket, msg):
    # 确保数据目录存在
    os.makedirs(DATA_DIR, exist_ok=True)
    try:
        user_id = str(msg.get("user_id"))
        group_id = str(msg.get("group_id"))
        raw_message = str(msg.get("raw_message"))
        role = str(msg.get("sender", {}).get("role"))
        message_id = str(msg.get("message_id"))
        authorized = user_id in owner_id

        # 开关
        if raw_message == "gl":
            await toggle_function_status(websocket, group_id, message_id, authorized)
            return

        # 检查是否开启
        if load_function_status(group_id):

            if await add_group_link(
                websocket, group_id, message_id, raw_message, authorized
            ):
                return

            if await delete_group_link(
                websocket, group_id, message_id, raw_message, authorized
            ):
                return

            await send_group_link_message(websocket, user_id, group_id, raw_message)
    except Exception as e:
        logging.error(f"处理GroupLink群消息失败: {e}")
        await send_group_msg(
            websocket,
            group_id,
            "处理GroupLink群消息失败，错误信息：" + str(e),
        )
        return


# 回应事件处理函数
async def handle_GroupLink_response_message(websocket, message):
    try:
        msg = json.loads(message)

        if msg.get("status") == "ok":
            echo = msg.get("echo")

            if echo and echo.startswith("xxx"):
                pass
    except Exception as e:
        logging.error(f"处理GroupLink回应事件时发生错误: {e}")


# 统一事件处理入口
async def handle_events(websocket, msg):
    """统一事件处理入口"""
    post_type = msg.get("post_type", "response")  # 添加默认值
    try:
        # 处理回调事件
        if msg.get("status") == "ok":
            await handle_GroupLink_response_message(websocket, msg)
            return

        post_type = msg.get("post_type")

        # 处理元事件
        if post_type == "meta_event":
            await handle_GroupLink_meta_event(websocket)

        # 处理消息事件
        elif post_type == "message":
            message_type = msg.get("message_type")
            if message_type == "group":
                await handle_GroupLink_group_message(websocket, msg)
            elif message_type == "private":
                return

        # 处理通知事件
        elif post_type == "notice":
            if msg.get("notice_type") == "group":
                return

    except Exception as e:
        error_type = {
            "message": "消息",
            "notice": "通知",
            "request": "请求",
            "meta_event": "元事件",
        }.get(post_type, "未知")

        logging.error(f"处理GroupLink{error_type}事件失败: {e}")

        # 发送错误提示
        if post_type == "message":
            message_type = msg.get("message_type")
            if message_type == "group":
                await send_group_msg(
                    websocket,
                    msg.get("group_id"),
                    f"处理GroupLink{error_type}事件失败，错误信息：{str(e)}",
                )
            elif message_type == "private":
                await send_private_msg(
                    websocket,
                    msg.get("user_id"),
                    f"处理GroupLink{error_type}事件失败，错误信息：{str(e)}",
                )
