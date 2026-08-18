import os
from dataclasses import dataclass
from dotenv import load_dotenv


load_dotenv()


@dataclass
class RDBCredential:
    def get_connection_string(self):
        pass