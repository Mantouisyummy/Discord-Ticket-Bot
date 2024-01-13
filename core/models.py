from sqlalchemy import Column, Integer, String

from . import database

class Ticket(database.Base):
    __tablename__ = "ticket"

    guild_id = Column(Integer, primary_key=True)
    ticket_channel_id = Column(Integer, primary_key=True)
    log_channel_id = Column(Integer, primary_key=True)
    ticket_message_id = Column(Integer, primary_key=True)
    ticket_name = Column(String, primary_key=True)
    webhook_url = Column(String, primary_key=True)
    