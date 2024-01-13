from disnake.ui import View

class TicketView(View):
    def __init__(self) -> None:
        super().__init__(timeout=None)