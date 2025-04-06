from pkg.plugin.context import register, handler, llm_func, BasePlugin, APIHost, EventContext
from pkg.plugin.events import *  # 导入事件类
import re

"""
收到消息时，移除消息中的所有XML标签及其内容，包括：
<think>、<details>、<summary>、<thinking> 和文末的 <sources> 标签
"""

# 注册插件
@register(name="RemoveXMLTags", description="移除消息中的所有XML标签及其内容，包括<think>,<details>,<summary>,<thinking>和<sources>", version="1.0",
          author="the-lazy-me")
class RemoveXMLTagsPlugin(BasePlugin):

    # 插件加载时触发
    def __init__(self, host: APIHost):
        super().__init__(host)  # 必须调用父类的初始化方法

    # 异步初始化
    async def initialize(self):
        pass

    def remove_tags_content(self, msg: str) -> str:
        """
        移除消息中的所有XML标签及其内容
        """
        # 处理完整标签对（跨行匹配）
        msg = re.sub(r'<think\b[^>]*>[\s\S]*?</think>',
                     '', msg, flags=re.DOTALL | re.IGNORECASE)
        msg = re.sub(
            r'<details\b[^>]*>[\s\S]*?</details>', '', msg, flags=re.DOTALL | re.IGNORECASE)
        msg = re.sub(
            r'<summary\b[^>]*>[\s\S]*?</summary>', '', msg, flags=re.DOTALL | re.IGNORECASE)
        msg = re.sub(
            r'<thinking\b[^>]*>[\s\S]*?</thinking>', '', msg, flags=re.DOTALL | re.IGNORECASE)
        # 新增：处理sources标签（通常在文末）
        msg = re.sub(
            r'<sources\b[^>]*>[\s\S]*?</sources>', '', msg, flags=re.DOTALL | re.IGNORECASE)

        # 清理残留标签（包括未闭合的标签和单独的结束标签）
        tags = ['think', 'details', 'summary', 'thinking', 'sources']  # 新增sources
        for tag in tags:
            # 处理未闭合的开始标签
            msg = re.sub(r'<{}\b[^>]*>[\s\S]*?(?=<|$)'.format(tag), '', msg, flags=re.IGNORECASE)
            # 处理单独的结束标签
            msg = re.sub(r'</{}>'.format(tag), '', msg, flags=re.IGNORECASE)
            # 处理开始标签（无论是否有内容）
            msg = re.sub(r'<{}\b[^>]*>'.format(tag), '', msg, flags=re.IGNORECASE)

        # 优化换行处理：合并相邻空行但保留段落结构
        msg = re.sub(r'\n{3,}', '\n\n', msg)  # 三个以上换行转为两个
        msg = re.sub(r'(\S)\n{2,}(\S)', r'\1\n\2', msg)  # 正文间的多个空行转为单个
        return msg.strip()

    # 当收到回复消息时触发
    @handler(NormalMessageResponded)
    async def normal_message_responded(self, ctx: EventContext):
        # 检查所有支持的标签，包括新增的sources
        target_tags = ["<think>", "<details>", "<summary>", "<thinking>", "<sources>"]
        msg = ctx.event.response_text
        if any(tag.lower() in msg.lower() for tag in target_tags):
            processed_msg = self.remove_tags_content(msg)
            if processed_msg:
                ctx.add_return("reply", [processed_msg])
            else:
                self.ap.logger.warning("处理后的消息为空，跳过回复")

    # 插件卸载时触发
    def __del__(self):
        pass
