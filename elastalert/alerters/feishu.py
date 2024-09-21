import json
import requests
import time
from datetime import datetime

from elastalert.alerts import Alerter, DateTimeEncoder
from elastalert.util import elastalert_logger, EAException
from requests.exceptions import RequestException


class FeishuAlert(Alerter):

    required_options = frozenset(
        ['feishualert_botid', "feishualert_title", "alert_text"])

    def __init__(self, rule: dict):
        super(FeishuAlert, self).__init__(rule)
        self.url = self.rule.get(
            "feishualert_url", "https://open.feishu.cn/open-apis/bot/v2/hook/")
        self.bot_id = self.rule.get("feishualert_botid", "")
        self.title = self.rule.get("feishualert_title", "")
        self.body = self.create_alert_body(self.rule.get("feishualert_body", ""))
        self.skip = self.rule.get("feishualert_skip", {})
        if not self.bot_id or not self.title or not self.body:
            raise EAException("Configure botid|title|body is invalid")

    def get_info(self) -> dict:
        return {
            "type": "FeishuAlert"
        }

    def get_rule(self) -> dict:
        return self.rule

    def alert(self, matches: list):
        now = datetime.now().strftime("%H:%M:%S")
        if "start" in self.skip and "end" in self.skip:
            if self.skip["start"] <= now <= self.skip["end"]:
                elastalert_logger.info("Skip match in silence time...")
                return

        headers = {
            "Content-Type": "application/json",
        }
        body = {
            "msg_type": "text",
            "content": {
                "title": self.title,
                "text": self.body
            }
        }

        if matches:
            print("🚀 ~ file: feishu.py:54 ~ matches:", matches)
            try:
                self.rule["feishualert_time"] = datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S")
                merge = {**matches[0], **self.rule}
                body["content"]["text"] = self.create_alert_body(self.body.format(**merge))
            except Exception as e:
                elastalert_logger.error(f"Error formatting message: {e}")

        try:
            url = f"{self.url}{self.bot_id}"
            print(json.dumps(body))
            # res = requests.post(url=url, data=json.dumps(body), headers=headers)
            # res.raise_for_status()
        except RequestException as e:
            raise EAException(f"Error request to feishu: {e}")
