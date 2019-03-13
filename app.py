import time
import json
from slackclient import SlackClient
from dateutil import parser
from datetime import datetime
import schedule

# load configurations
config = json.loads(open("./config.json").read())

API_TOKEN = config["slack"]["apiToken"]
CLIENT_ID = config["slack"]["clientId"]
CLIENT_SECRET = config["slack"]["clientSecret"]
VERIFICATION_TOKEN = config["slack"]["verificationToken"]
CHANNEL_ID = config["slack"]["channelId"]

YOUR_NAME = config["bot"]["yourName"]
NOTIFY_AT = config["bot"]["notifyAt"]
START_DATE = parser.parse(config["bot"]["startDate"])
END_DATE = parser.parse(config["bot"]["endDate"])

START_IMG = "https://i.imgur.com/PkbKJY1.jpg"  # 시작 메세지 이미지
DAILY_BEFORE_ENLISTMENT_IMG = "https://i.imgur.com/uM1dyrM.png"  # 군입대 전 메세지 이미지
DAILY_AFTER_ENLISTMENT_IMG = "https://i.imgur.com/U059WfE.png"  # 군입대 후 메세지 이미지


# init slack client
sc = SlackClient(API_TOKEN)


def _format_date(date):
    return date.strftime("%Y년 %m월 %d일")


def _calc_total_days():
    # 총 군복무 일 수
    total_days = (END_DATE - START_DATE).days
    return total_days


def _calc_remaining_days():
    # 남은 군복무 일 수
    remaining_days = (END_DATE - datetime.now()).days
    return remaining_days


def _calc_after_enlistment_days():
    # 군 입대후 지난 일 수. 음수라면 입대 전
    after_enlistment_days = (datetime.now() - START_DATE).days
    return after_enlistment_days


def _calc_percentage():
    # 복무율
    percentage = round(
        (_calc_after_enlistment_days() / _calc_total_days()) * 100, 2)
    return percentage


def _render_progress_bar():
    # 텍스트 프로그레스바
    total_squares = 20
    filled_squares = round(_calc_percentage() / (100 / total_squares))
    unfilled_squares = total_squares - filled_squares

    progress_bar = ""

    for i in range(filled_squares):
        progress_bar = progress_bar + "█ "

    for i in range(unfilled_squares):
        progress_bar = progress_bar + "▒ "

    return progress_bar


def send_start_message():
    formatted_start_date = _format_date(START_DATE)
    formatted_end_date = _format_date(END_DATE)

    sc.api_call(
        "chat.postMessage",
        channel=CHANNEL_ID,
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "복무봇이 시작되었습니다. :sob:"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": "*장병이름*\n{}".format(YOUR_NAME)
                    },
                    {
                        "type": "mrkdwn",
                        "text": "*알림시각*\n{}시".format(NOTIFY_AT)
                    },
                    {
                        "type": "mrkdwn",
                        "text": "*복무 시작일*\n{}".format(formatted_start_date)
                    },
                    {
                        "type": "mrkdwn",
                        "text": "*복무 종료일*\n{}".format(formatted_end_date)
                    }
                ],
                "accessory": {
                    "type": "image",
                    "image_url": START_IMG,
                    "alt_text": "plants"
                }
            },
            {
                "type": "context",
                "elements": [
                        {
                            "type": "plain_text",
                            "text": "Developed by Hudi (https://hudi.kr)",
                        }
                ]
            }
        ]
    )


def _send_daily_message_before_enlistment():
    formatted_today_date = _format_date(datetime.now())
    formatted_start_date = _format_date(START_DATE)
    formatted_end_date = _format_date(END_DATE)

    total_days = _calc_total_days()
    after_enlistment_days = _calc_after_enlistment_days()

    sc.api_call(
        "chat.postMessage",
        channel=CHANNEL_ID,
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "`{}` 오늘, *{}* 님은 입대까지 {}일 남았습니다.\n\n".format(formatted_today_date, YOUR_NAME, -after_enlistment_days)
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": "*복무 시작일*\n{}".format(formatted_start_date)
                    },
                    {
                        "type": "mrkdwn",
                        "text": "*복무 종료일*\n{}".format(formatted_end_date)
                    },
                    {
                        "type": "mrkdwn",
                        "text": "*총 복무일*\n{}일".format(total_days)
                    },
                    {
                        "type": "mrkdwn",
                        "text": "*입대까지*\n{}일".format(-after_enlistment_days)
                    }
                ],
                "accessory": {
                    "type": "image",
                    "image_url": DAILY_BEFORE_ENLISTMENT_IMG,
                    "alt_text": "plants"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "plain_text",
                        "text": "Developed by Hudi (https://hudi.kr)",
                        "emoji": True
                    }
                ]
            }
        ]
    )


def _send_daily_message_after_enlistment():
    formatted_today_date = _format_date(datetime.now())
    formatted_start_date = _format_date(START_DATE)
    formatted_end_date = _format_date(END_DATE)

    percentage = _calc_percentage()
    progress_bar = _render_progress_bar()
    total_days = _calc_total_days()
    after_enlistment_days = _calc_after_enlistment_days()
    remaining_days = _calc_remaining_days()

    sc.api_call(
        "chat.postMessage",
        channel=CHANNEL_ID,
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "`{}` 오늘, *{}* 님의 복무율 \n\n 복무율 *{}%* |  {} | *{}일 / {}일*".format(formatted_today_date, YOUR_NAME, percentage, progress_bar, after_enlistment_days, total_days)
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": "*복무 시작일*\n{}".format(formatted_start_date)
                    },
                    {
                        "type": "mrkdwn",
                        "text": "*복무 종료일*\n{}".format(formatted_end_date)
                    },
                    {
                        "type": "mrkdwn",
                        "text": "*총 복무일*\n{}일".format(total_days)
                    },
                    {
                        "type": "mrkdwn",
                        "text": "*현재 복무일*\n{}일".format(after_enlistment_days)
                    },
                    {
                        "type": "mrkdwn",
                        "text": "*남은 복무일*\n{}일".format(remaining_days)
                    }
                ],
                "accessory": {
                    "type": "image",
                    "image_url": DAILY_AFTER_ENLISTMENT_IMG,
                    "alt_text": "plants"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "plain_text",
                        "text": "Developed by Hudi (https://hudi.kr)",
                        "emoji": True
                    }
                ]
            }
        ]
    )


def send_daily_message():
    after_enlistment_days = _calc_after_enlistment_days()
    if (after_enlistment_days < 0):
        _send_daily_message_before_enlistment()
    else:
        _send_daily_message_after_enlistment()

    print("[복무봇] 현재 복무율 전송")


if __name__ == '__main__':
    notify_at = "{}:00".format(str(NOTIFY_AT).zfill(2))

    print("[복무봇] 실행 준비중...")

    send_start_message()
    print("[복무봇] 실행 메세지 전송")

    send_daily_message()
    print("[복무봇] 현재 복무율 최초 전송")
    # 봇 실행시 최초 실행

    # 스케줄 시작
    schedule.every().day.at(notify_at).do(send_daily_message)
    print("[복무봇] 복무봇 스케줄 설정: {} 마다 실행".format(notify_at))

    print("[복무봇] 스케줄링 시작!")
    while True:
        schedule.run_pending()
        time.sleep(1)
