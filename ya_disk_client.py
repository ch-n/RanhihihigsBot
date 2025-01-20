import json

from yadisk import YaDisk
from yadisk.exceptions import YaDiskError

class YaDiskClient:
    def __init__(self, token):
        self.token = token
        self.disk = YaDisk(token=token)

    async def check_token_validity(self):
        disk = YaDisk(token=self.token)
        try:
            if disk.check_token():
                return True
            else:
                return False
        except YaDiskError as e:
            return False

    async def get_json_of_items_dates_from_yandex_disk(self, directory_path):
        y = YaDisk(token=self.token)

        if not await self.check_token_validity():
            return None

        try:
            items = y.listdir(f"disk:/{directory_path}")
        except Exception as e:
            return None

        if not items:
            return None

        modified_times = {f"item_{i}": item.modified.isoformat() for i, item in enumerate(items)}

        return json.dumps(modified_times, ensure_ascii=False)