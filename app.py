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
BOT_TOKEN = config["slack"]["botToken"]
CHANNEL_ID = config["slack"]["channelId"]

YOUR_NAME = config["bot"]["yourName"]
NOTIFY_AT = config["bot"]["notifyAt"]
START_DATE = parser.parse(config["bot"]["startDate"])
END_DATE = parser.parse(config["bot"]["endDate"])


# init slack client
sc = SlackClient(API_TOKEN)

# sc.api_call(
#     "channels.join",
#     channel=CHANNEL_ID
# )

# sc.api_call(
#     "chat.postMessage",
#     channel=CHANNEL_ID,
#     text="Hello from Python! :point_right:"
# )


def format_date(date):
    return date.strftime("%Y년 %m월 %d일")


def calc_total_days():
    # 총 군복무 일 수
    total_days = (END_DATE - START_DATE).days
    return total_days


def calc_remaining_days():
    # 남은 군복무 일 수
    remaining_days = (END_DATE - datetime.now()).days
    return remaining_days


def calc_after_enlistment_days():
    # 군 입대후 지난 일 수. 음수라면 입대 전
    after_enlistment_days = (datetime.now() - START_DATE).days
    return after_enlistment_days


def calc_percentage():
    # 복무율
    percentage = round(
        (calc_after_enlistment_days() / calc_total_days()) * 100, 2)
    return percentage


def render_progress_bar():
    # 텍스트 프로그레스바
    total_squares = 20
    filled_squares = round(calc_percentage() / (100 / total_squares))
    unfilled_squares = total_squares - filled_squares

    progress_bar = ""

    for i in range(filled_squares):
        progress_bar = progress_bar + "█ "

    for i in range(unfilled_squares):
        progress_bar = progress_bar + "▒ "

    return progress_bar


def send_start_message():
    formatted_start_date = format_date(START_DATE)
    formatted_end_date = format_date(END_DATE)

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
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": "*장병이름*\n{}".format(YOUR_NAME)
                    },
                    {
                        "type": "mrkdwn",
                        "text": "*알림시각*\n오전 9시"
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
                    "image_url": "https://i.imgur.com/PkbKJY1.jpg",
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
    formatted_today_date = format_date(datetime.now())
    formatted_start_date = format_date(START_DATE)
    formatted_end_date = format_date(END_DATE)

    total_days = calc_total_days()
    after_enlistment_days = calc_after_enlistment_days()

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
                    "image_url": "https://i.imgur.com/uM1dyrM.png",
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
    formatted_today_date = format_date(datetime.now())
    formatted_start_date = format_date(START_DATE)
    formatted_end_date = format_date(END_DATE)

    percentage = calc_percentage()
    progress_bar = render_progress_bar()
    total_days = calc_total_days()
    after_enlistment_days = calc_after_enlistment_days()

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
                    }
                ],
                "accessory": {
                    "type": "image",
                    "image_url": "https://i.imgur.com/U059WfE.png",
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
    after_enlistment_days = calc_after_enlistment_days()
    if (after_enlistment_days < 0):
        _send_daily_message_before_enlistment()
    else:
        _send_daily_message_after_enlistment()


if __name__ == '__main__':
    send_start_message()
    send_daily_message()
    schedule.every().day.at("{}:00".format(NOTIFY_AT)).do(send_daily_message)
    while True:
        schedule.run_pending()
        time.sleep(1)
