# 群互联消息屏蔽配置

# 不转发的消息前缀列表
BLOCKED_MESSAGE_PREFIXES = [
    "选课查询",
    "平均分",
]

# 不转发的消息内容列表（支持部分匹配）
BLOCKED_MESSAGE_CONTENTS = [
    "CQ:json,data=",  # JSON卡片消息
]

# 不转发的命令列表（精确匹配）
BLOCKED_COMMANDS = [
    "gl",
    "add互联",
    "rm互联",
]

# 不转发的正则表达式列表
BLOCKED_REGEX_PATTERNS = [
    r"这是来自「WakeUp课程表」的课表分享，30分钟内有效哦，如果失效请朋友再分享一遍叭。为了保护隐私我们选择不监听你的剪贴板，请复制这条消息后，打开App的主界面，右上角第二个按钮 -> 从分享口令导入，按操作提示即可完成导入~分享口令为「.*」",
]
