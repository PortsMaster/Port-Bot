import requests
import json
from random import choice
import os
import datetime

# --- CONFIGURATION ---
WEBHOOK_URL = os.environ.get("NEWS_WEBHOOK_URL")
if not WEBHOOK_URL:
    raise ValueError("NEWS_WEBHOOK_URL environment variable not set.")

PORTS_DATABASE_URL = "https://raw.githubusercontent.com/PortsMaster/PortMaster-Info/main/ports.json"
LOCAL_PORTS_FILE = "ports.json"

SCREENSHOT_URL_MAIN = "https://raw.githubusercontent.com/PortsMaster/PortMaster-New/main/ports/"
SCREENSHOT_URL_MULTIVERSE = "https://raw.githubusercontent.com/PortsMaster-MV/PortMaster-MV-New/main/ports/"

EMOJIS = ["🎉", "🍾", "🎊", "🎇", "🥂", "🎈", "🥳", "🎆", "🧨", "🤯", "💥", "🔥", "🎮", "🕹️", "👾", "✨", "🌟", "🤩", "🚀", "🎁"]
BOT_USERNAME = "Announcement Bot"
EMBED_COLOR = 3447003  # A nice PortMaster blue

ANNOUNCEMENT_MESSAGES = [
    "A new port has arrived! **{title}** is now available on PortMaster!",
    "Check out the latest addition! **{title}** just landed on PortMaster!",
    "Fresh off the press! You can now grab **{title}** on PortMaster!",
    "Get ready to play! **{title}** has just been released on PortMaster!",
    "Heads up, everyone! **{title}** is the newest port available!",
    "Surprise! **{title}** has just dropped on PortMaster!",
    "Hold onto your hats! **{title}** is now playable on PortMaster!",
    "The port collection grows! Welcome, **{title}**!",
    "It's here! **{title}** has officially joined the PortMaster library.",
    "New game alert! **{title}** has been added to PortMaster.",
    "Power up your devices! **{title}** is ready for download on PortMaster.",
]

THANKS_MESSAGES = [
    "Thanks to {porters_md} for bringing this game to PortMaster!",
    "A big thank you to {porters_md} for their work on this port!",
    "Shout-out to {porters_md} for making this release possible!",
    "This port was made possible by the talented {porters_md}!",
    "Let's give a round of applause to {porters_md} for this one!",
    "Huge props to {porters_md} for porting this over!",
]

# --- DISCORD WEBHOOK FUNCTION ---
def post_announcement(content, embed_data):
    """
    Posts a message with a rich embed to the configured Discord webhook.
    """
    embed_data["timestamp"] = datetime.datetime.utcnow().isoformat()
    embed_data["color"] = EMBED_COLOR

    payload = {
        "username": BOT_USERNAME,
        "content": content,
        "embeds": [embed_data],
    }

    try:
        response = requests.post(WEBHOOK_URL, json=payload, timeout=10)
        response.raise_for_status()
        print(f"Successfully posted announcement for: {embed_data.get('title', 'Unknown Port')}")
    except requests.exceptions.RequestException as e:
        print(f"Error posting to Discord: {e}")


# --- DATA HANDLING FUNCTIONS ---
def get_latest_ports():
    """
    Fetches the latest ports data from the PortMaster GitHub.
    """
    try:
        response = requests.get(PORTS_DATABASE_URL, timeout=10)
        response.raise_for_status()
        return response.json().get("ports", {})
    except requests.exceptions.RequestException as e:
        print(f"Error fetching latest ports data: {e}")
        return {}
    except json.JSONDecodeError:
        print("Error decoding JSON from ports data.")
        return {}


def get_announced_ports():
    """
    Loads the list of previously announced ports from a local file.
    """
    try:
        with open(LOCAL_PORTS_FILE, "r", encoding="utf8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_announced_ports(ports_list):
    """
    Saves the updated list of announced ports to a local file.
    """
    with open(LOCAL_PORTS_FILE, "w", encoding="utf8") as f:
        json.dump(ports_list, f, indent=2, sort_keys=True)


# --- MAIN LOGIC ---
def main():
    """
    Main function to check for new ports and announce them.
    """
    latest_ports = get_latest_ports()
    if not latest_ports:
        print("No ports data fetched. Exiting.")
        return

    announced_ports = get_announced_ports()

    # If the local file is empty, initialize it with the current ports list to avoid announcing all of them.
    if not announced_ports:
        print("No previously announced ports found. Initializing with current port list.")
        save_announced_ports(list(latest_ports.keys()))
        return

    newly_announced_ports = list(announced_ports)

    # Sort ports by title to ensure a consistent order, though we only announce one.
    sorted_ports = sorted(latest_ports.items())

    for port_name, port_info in sorted_ports:
        if port_name not in announced_ports:
            print(f"New port found: {port_name}")

            attr = port_info.get("attr", {})
            source = port_info.get("source", {})

            # --- Extract Data ---
            title = attr.get("title", port_name.replace(".zip", ""))
            description = attr.get("desc", "No description available.")
            porters_list = attr.get("porter", ["N/A"])
            porters_md = ", ".join(f"**{p}**" for p in porters_list)

            genres_list = attr.get("genres", [])
            genres = ", ".join(g.title() for g in genres_list) if genres_list else "N/A"

            is_rtr = "✅ Yes" if attr.get("rtr") else "❌ No"
            install_notes = attr.get("inst")

            # --- Build URLs ---
            img_filename = attr.get("image", {}).get("screenshot")
            img_url = None
            if img_filename:
                base_url = SCREENSHOT_URL_MAIN if source.get("repo") != "multiverse" else SCREENSHOT_URL_MULTIVERSE
                img_url = f"{base_url}{port_name.replace('.zip', '/')}{img_filename}"

            detail_url = f"https://portmaster.games/detail.html?name={port_name.replace('.zip', '')}"

            # --- Construct Embed ---
            message_template = choice(ANNOUNCEMENT_MESSAGES)
            post_content = f"{choice(EMOJIS)} {message_template.format(title=title)} {choice(EMOJIS)}"

            thanks_template = choice(THANKS_MESSAGES)
            thanks_message = thanks_template.format(porters_md=porters_md)

            embed = {
                "title": title,
                "url": detail_url,
                "description": f"{description}\n\n{thanks_message}",
                "fields": [
                    {"name": "Porters", "value": ", ".join(porters_list), "inline": False},
                    {"name": "Genres", "value": genres, "inline": True},
                    {"name": "Ready to Run", "value": is_rtr, "inline": True},
                ]
            }

            if install_notes:
                embed["fields"].append({"name": "Notes", "value": install_notes, "inline": False})

            if img_url:
                embed["image"] = {"url": img_url}

            # --- Post and Update ---
            post_announcement(post_content, embed)
            newly_announced_ports.append(port_name)

            # Save after each announcement to prevent re-announcing if the script fails mid-run
            save_announced_ports(newly_announced_ports)

            # Announce one port per run
            print("Announcement posted. Exiting.")
            return

    print("No new ports to announce. Check complete.")


if __name__ == "__main__":
    main()
