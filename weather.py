import requests  # 导入用于发送 HTTP 请求的库
import json  # 导入用于处理 JSON 数据的库
import re  # 导入用于正则表达式匹配的库
import plugins  # 导入自定义的插件模块
from bridge.reply import Reply, ReplyType  # 导入用于构建回复消息的类
from plugins import *  # 导入其他自定义插件
from config import conf  # 导入配置文件

@plugins.register(
    name="weather",  # 插件的名称
    desire_priority=1,  # 插件的优先级
    hidden=False,  # 插件是否隐藏
    desc="A plugin for weather",  # 插件的描述
    version="0.0.1",  # 插件的版本号
    author="fatwang2",  # 插件的作者
)
class weather(Plugin):
    def __init__(self):
        super().__init__()
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        print("[weather] inited")  # 初始化插件时打印一条消息

    def on_handle_context(self, e_context: EventContext):
        content = e_context["context"].content  # 获取事件上下文中的消息内容
    
        if content.startswith("天气 "):
            parts = content.split(" ")
            if len(parts) > 1:
                city = parts[1]  # 获取城市名称
                app_id = conf().get("weather_app_id")  # 从配置文件中获取 app_id
                app_secret = conf().get("weather_app_secret")  # 从配置文件中获取 app_secret
                # 构建完整的请求URL
                url = f"https://www.mxnzp.com/api/weather/current/{city}?app_id={app_id}&app_secret={app_secret}"

            try:
                response = requests.get(url)  # 发送 get 请求
                response.raise_for_status()  # 抛出异常
            except requests.exceptions.RequestException as e:
                print(f"An error occurred when making the request: {e}")  # 请求出错时打印错误消息
                return

            data = json.loads(response.text)  # 解析返回的 JSON 数据
            weather_data = data.get('data')  # 获取"data"键下的内容
            if weather_data:
                address = weather_data.get('address', '未知地点')
                temp = weather_data.get('temp', '未知温度')
                weather = weather_data.get('weather', '未知天气')
                windDirection = weather_data.get('windDirection', '未知风向')
                windPower = weather_data.get('windPower', '未知风力')
                humidity = weather_data.get('humidity', '未知湿度')
                reportTime = weather_data.get('reportTime', '未知时间')

                reply = Reply()  # 创建回复消息对象
                reply.type = ReplyType.TEXT  # 设置回复消息的类型为文本
                reply.content = f"🌦 天气信息 ({address})\n"
                reply.content += f"🌡 温度: {temp}\n"
                reply.content += f"🌫 天气: {weather}\n"
                reply.content += f"🌬 风向: {windDirection}\n"
                reply.content += f"💨 风力: {windPower}\n"
                reply.content += f"💧 湿度: {humidity}\n"
                reply.content += f"🕒 更新时间: {reportTime}\n"

                e_context["reply"] = reply
                e_context.action = EventAction.BREAK_PASS
            else:
                print("ERROR: Data not found in response")

    def get_help_text(self, **kwargs):
        help_text = "输入 '天气'，我会为你推送今日天气\n"
        return help_text
