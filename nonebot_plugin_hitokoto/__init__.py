import httpx

from nonebot import logger, get_plugin_config
from nonebot.plugin import on_command
from pydantic import BaseModel

class ScopeConfig(BaseModel):
    c: list[str] = []
    """句子类型"""
    base_url: str = "https://international.v1.hitokoto.cn"
    """请求地址"""
    priority: int = 10
    """指令优先级"""

class Config(BaseModel):
    hitokoto: ScopeConfig = ScopeConfig()

plugin_config = get_plugin_config(Config).hitokoto


hitokoto_matcher = on_command("一言", aliases={"一句"}, block=True, priority=plugin_config.priority)

def generate_url() -> str:
    """构建请求url"""
    data = f"{plugin_config.base_url}?"
    for c in plugin_config.c:
        data += f"c={c}&"
    return data.strip("&")

@hitokoto_matcher.handle()
async def hitokoto():
    async with httpx.AsyncClient() as client:
        response = await client.get(generate_url())

    if response.is_error:
        error_msg = "获取一言失败"
        logger.error(error_msg)
        return error_msg
    
    data = response.json()
    msg = data["hitokoto"]
    add = ""
    if works := data["from"]:
        add += f"《{works}》"
    if from_who := data["from_who"]:
        add += f"{from_who}"
    if add:
        msg += f"\n——{add}"

    await hitokoto_matcher.finish(msg)
