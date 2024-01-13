from datetime import datetime
from typing import Any
from disnake import Embed
from disnake.colour import Colour
from disnake.types.embed import EmbedType

# pylint: disable=C0116
# pylint: disable=C0115

class SuccessEmbed(Embed):
    def __init__(self, title: str, description: str = None, **kwargs):
        super().__init__(title="✅ | " + title, description=description, color=0x0f9d58, **kwargs)
        self._files = {}

class LogEmbed(Embed):
    def __init__(self, name: str, created: str, subject: str, mode: str, closer: str = None, **kwargs):
        match mode:
            case "create":
                title = "客服單建立"
                description = f"""
                > **客服單**: {name}
                > **主題**: {subject}
                > **建立者**: {created}
                """
                color = Colour.green()
            case "close":
                title = "客服單關閉"
                description = f"""
                > **客服單**: {name}
                > **主題**: {subject}
                > **建立者**: {created}
                > **關閉者**: {closer}
                """
                self.set_footer(text="聊天紀錄已自動附在檔案中")
                color = Colour.red()
        super().__init__(title=title, description=description, color=color, timestamp=datetime.now(), **kwargs)

class InfoEmbed(Embed):
    def __init__(self, title: str, description: str = None, **kwargs):
        super().__init__(title="ℹ️ | " + title, description=description, color=0x4285f4, **kwargs)


class LoadingEmbed(Embed):
    def __init__(self, title: str, description: str = None, **kwargs):
        super().__init__(title="⌛ | " + title, description=description, color=0x4285F4, **kwargs)


class WarningEmbed(Embed):
    def __init__(self, title: str, description: str = None, **kwargs):
        super().__init__(title="⚠ | " + title, description=description, color=0xf4b400, **kwargs)


class ErrorEmbed(Embed):
    def __init__(self, title: str, description: str = None, **kwargs):
        super().__init__(title="❌ | " + title, description=description, color=0xdb4437, **kwargs)

class CloseEmbed(Embed):
    def __init__(self, title: str, description: str = None, **kwargs):
        super().__init__(title="🔒 | " + title, description=description, color=0xdb4437, **kwargs)
    
class HelpEmbed(Embed):
    def __init__(self, title: str, description: str = None, **kwargs):
        super().__init__(title=title, description=description, color=0xdb4437, **kwargs)
