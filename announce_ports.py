import requests
import json
from random import choice
import os

webhook_url = os.environ["NEWS_WEBHOOK_URL"]

screenshot_url_main = (
    "https://raw.githubusercontent.com/PortsMaster/PortMaster-New/main/ports/"
)
screenshot_url_multiverse = (
    "https://raw.githubusercontent.com/PortsMaster-MV/PortMaster-MV-New/main/ports/"
)


emojis = ["🎉","🍾","🎊","🎇","🥂","🎈","🥳","🎆","🧨","🤯","💥","🔥"]


def post_message(post_title, port_title, link, image,comment):
    # https://gist.github.com/Birdie0/78ee79402a4301b1faf412ab5f1cdcf9
    data = {
        "username": "Announcement Bot",
        "content": post_title,
        "embeds": [
            {
                "title": f"{port_title}",
                "url": f"{link}",
                "description": f"{comment}",
                "image": {"url": f"{image}"},
            }
        ],
    }

    response = requests.post(webhook_url, json=data)

newPorts = []

response = requests.get("https://raw.githubusercontent.com/PortsMaster/PortMaster-Info/main/ports.json")
portJson = response.json()
for port in portJson["ports"]:
    newPorts.append(port)


oldPorts = []

try:
    with open("ports.json") as portsjson:
        parsed_json = json.load(portsjson)
        for port in parsed_json:
            oldPorts.append(port)
except Exception as e:
    pass

if len(oldPorts) < 1:
    oldPorts = newPorts

with open("ports.json", "w", encoding="utf8") as outfile:
    for port in portJson["ports"]:
        if port not in oldPorts:
            title = portJson["ports"][port]["attr"]["title"]
            description = portJson["ports"][port]["attr"]["desc"]
            porter = ",".join(portJson["ports"][port]["attr"]["porter"])
            imgurl = (
                screenshot_url_main
                + port.replace(".zip", "/")
                + portJson["ports"][port]["attr"]["image"]["screenshot"]
            )
            if portJson["ports"][port]["source"]["repo"] == "multiverse":
                imgurl = (
                    screenshot_url_multiverse
                    + port.replace(".zip", "/")
                    + portJson["ports"][port]["attr"]["image"]["screenshot"]
                )
            link = "https://portmaster.games/detail.html?name=" + port.replace(
                ".zip", ""
            )
            thanks = f"\n\n Thanks to {porter} for bringing this game to PortMaster"
            comment = description + thanks
            oldPorts.append(port)
            post_message(
                post_title=f"{choice(emojis)} {title} is now on PortMaster! {choice(emojis)}",
                port_title=title,
                link=link,
                image=imgurl,
                comment=comment
            )
            break

    outfile.write(json.dumps(oldPorts, indent=2, sort_keys=True))
