import requests
import json
from random import choice
import os
from typing import Dict, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
WEBHOOK_URL = os.environ["NEWS_WEBHOOK_URL"]
SCREENSHOT_URL_MAIN = "https://raw.githubusercontent.com/PortsMaster/PortMaster-New/main/ports/"
SCREENSHOT_URL_MULTIVERSE = "https://raw.githubusercontent.com/PortsMaster-MV/PortMaster-MV-New/main/ports/"
PORTS_JSON_URL = "https://raw.githubusercontent.com/PortsMaster/PortMaster-Info/main/ports.json"
LOCAL_PORTS_FILE = "ports.json"
EMOJIS = ["🎉", "🍾", "🎊", "🎇", "🥂", "🎈", "🥳", "🎆", "🧨", "🤯", "💥", "🔥"]

def post_message(post_title: str, port_title: str, link: str, image: str, comment: str) -> None:
    """Post a message to Discord webhook."""
    data = {
        "username": "Announcement Bot",
        "content": post_title,
        "embeds": [{
            "title": port_title,
            "url": link,
            "description": comment,
            "image": {"url": image}
        }]
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=data)
        response.raise_for_status()
        logging.info(f"Successfully posted announcement for {port_title}")
    except requests.RequestException as e:
        logging.error(f"Failed to post announcement for {port_title}: {e}")

def fetch_ports() -> Dict:
    """Fetch and return the ports data from the remote JSON file."""
    try:
        response = requests.get(PORTS_JSON_URL)
        response.raise_for_status()
        return response.json()["ports"]
    except requests.RequestException as e:
        logging.error(f"Failed to fetch ports data: {e}")
        return {}

def load_old_ports() -> List[str]:
    """Load the list of old ports from the local JSON file."""
    try:
        with open(LOCAL_PORTS_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        logging.warning(f"Failed to load {LOCAL_PORTS_FILE}, starting with empty list")
        return []

def save_ports(ports: List[str]) -> None:
    """Save the list of ports to the local JSON file."""
    try:
        with open(LOCAL_PORTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(ports, f, indent=2, sort_keys=True)
        logging.info(f"Successfully saved ports to {LOCAL_PORTS_FILE}")
    except IOError as e:
        logging.error(f"Failed to save ports: {e}")

def get_image_url(port: str, port_data: Dict) -> str:
    """Generate the correct image URL based on the port's source."""
    base_url = SCREENSHOT_URL_MULTIVERSE if port_data["source"]["repo"] == "multiverse" else SCREENSHOT_URL_MAIN
    return f"{base_url}{port.replace('.zip', '/')}{port_data['attr']['image']['screenshot']}"

def main():
    new_ports = fetch_ports()
    old_ports = load_old_ports()

    for port, port_data in new_ports.items():
        if port not in old_ports:
            title = port_data["attr"]["title"]
            description = port_data["attr"]["desc"]
            porter = ", ".join(port_data["attr"]["porter"])
            image_url = get_image_url(port, port_data)
            link = f"https://portmaster.games/detail.html?name={port.replace('.zip', '')}"
            comment = f"{description}\n\nThanks to {porter} for bringing this game to PortMaster"

            post_message(
                post_title=f"{choice(EMOJIS)} {title} is now on PortMaster! {choice(EMOJIS)}",
                port_title=title,
                link=link,
                image=image_url,
                comment=comment
            )

            old_ports.append(port)
            save_ports(old_ports)
            break  # Remove this if you want to announce all new ports at once

if __name__ == "__main__":
    main()
