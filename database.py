from tinydb import TinyDB, where
from tinydb.table import Table

class Database:
    db: TinyDB
    guilds: Table

    def __init__(self):
        self.db = TinyDB('db.json')
        self.guilds = self.db.table('guilds')

    def get_guild(self, id):
        guild = self.guilds.get(where('id') == str(id))
        return guild and guild['data'] or None

    def set_guild(self, id, data):
        self.guilds.upsert({'id': str(id), 'data': data}, where('id') == str(id))

    def get_hacks(self):
        hacks = self.db.get(where('key') == 'hacks')
        return hacks and hacks['value'] or []

    def set_hacks(self, data):
        self.db.upsert({'key': 'hacks', 'value': data}, where('key') == 'hacks')

db = Database()
