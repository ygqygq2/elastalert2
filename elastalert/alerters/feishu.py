import json
import requests
from datetime import datetime
from requests.exceptions import RequestException

from elastalert.alerts import Alerter, DateTimeEncoder
from elastalert.util import elastalert_logger, EAException


class FeishuAlerter(Alerter):
    required_options = frozenset(['feishu_robot_webhook_url'])

    def __init__(self, rule: dict):
        super(FeishuAlerter, self).__init__(rule)
        self.url = self.rule.get("feishu_robot_webhook_url", "")
        self.skip = self.rule.get("feishu_skip", {})
        if not self.url:
            raise EAException("Configure feishu webhook url is invalid")

    def get_info(self) -> dict:
        return {
            "type": "Feishu"
        }

    def alert(self, matches: list):
        title = self.create_title(matches)
        # 处理 event.duration 的转换
        for match in matches:
            if 'event' in match and 'duration' in match['event']:
                match['event']['duration'] = float(match['event']['duration']) / 1e9
        # print("matches: ", matches)
        body = self.create_alert_body(matches)

        now = datetime.now().strftime("%H:%M:%S")
        if "start" in self.skip and "end" in self.skip:
            if self.skip["start"] <= now <= self.skip["end"]:
                elastalert_logger.info("Skip match in silence time...")
                return

        headers = {
            "Content-Type": "application/json",
        }
        payload = {
            "msg_type": "text",
            "content": {
                "title": title,
                "text": body
            }
        }

        try:
            res = requests.post(url=self.url, data=json.dumps(payload), headers=headers)
            res.raise_for_status()
        except RequestException as e:
            raise EAException(f"Error request to feishu: {e}")

        elastalert_logger.info("Trigger sent to Feishu")
