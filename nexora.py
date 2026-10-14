#!/usr/bin/env python3
"""
Nexora - CLI Setup & Launcher
Configures settings securely into config.json and launches Nexora Monitoring
"""

import os
import sys
import time
import json
import subprocess
from colorama import init, Fore, Style

init(autoreset=True)

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

ascii_art = f"""{Fore.GREEN} 
                                                       ╔═════════════════════════════════════════════════════╗
                                                       ║ ███╗   ██╗███████╗██╗  ██╗ ██████╗ ██████╗  █████╗  ║
                                                       ║ ████╗  ██║██╔════╝╚██╗██╔╝██╔═══██╗██╔══██╗██╔══██╗ ║
                                                       ║ ██╔██╗ ██║█████╗   ╚███╔╝ ██║   ██║██████╔╝███████║ ║
                                                       ║ ██║╚██╗██║██╔══╝   ██╔██╗ ██║   ██║██╔══██╗██╔══██║ ║
                                                       ║ ██║ ╚████║███████╗██╔╝ ██╗╚██████╔╝██║  ██║██║  ██║ ║
                                                       ║ ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝ ║
                                                       ╚═══════════════════════════════════════════˗ˏˋ ♡ ˎˊ˗ 

                                                      {Fore.WHITE}  by Ahlan Mira    github : https://github.com/Ahlan06

                                                           Created for cybersecurity learning and research.

                                                                             LOADING ...
{Style.RESET_ALL}
"""

ascii_art2 = f"""{Fore.RED}{Style.BRIGHT}
                                                       ╔═════════════════════════════════════════════════════╗
                                                       ║ ███╗   ██╗███████╗██╗  ██╗ ██████╗ ██████╗  █████╗  ║
                                                       ║ ████╗  ██║██╔════╝╚██╗██╔╝██╔═══██╗██╔══██╗██╔══██╗ ║
                                                       ║ ██╔██╗ ██║█████╗   ╚███╔╝ ██║   ██║██████╔╝███████║ ║
                                                       ║ ██║╚██╗██║██╔══╝   ██╔██╗ ██║   ██║██╔══██╗██╔══██║ ║
                                                       ║ ██║ ╚████║███████╗██╔╝ ██╗╚██████╔╝██║  ██║██║  ██║ ║
                                                       ║ ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝ ║
                                                       ╚═══════════════════════════════════════════˗ˏˋ ♡ ˎˊ˗ 


                                                                            NEXORA TOOL

                                                                  Developed for OSINT by Ahlan06 

                                                                github : https://github.com/Ahlan06

                               {Fore.WHITE}        This tool is for ethical and authorized use only — illegal use is strictly forbidden. 
{Style.RESET_ALL}
"""

def setup_nexora():
    clear_console()
    print(ascii_art)
    time.sleep(1.5)
    clear_console()
    print(ascii_art2)

    # 1. Configuration du Webhook Discord
    while True:
        try:
            webhook = input(f"{Fore.WHITE}Enter your Discord webhook URL : {Style.RESET_ALL}").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n{Fore.RED}[*] Operation cancelled by user.{Style.RESET_ALL}")
            return

        if not webhook:
            print(f"{Fore.RED}[!] Webhook cannot be empty.{Style.RESET_ALL}")
            continue

        if not (webhook.startswith("https://discord.com/api/webhooks/") or webhook.startswith("https://discordapp.com/api/webhooks/")):
            print(f"{Fore.YELLOW}[!] Warning: URL should start with https://discord.com/api/webhooks/{Style.RESET_ALL}")
            confirm = input(f"Do you want to keep this URL anyway? (y/n): ").strip().lower()
            if confirm == 'y':
                break
        else:
            break

    # 2. Intervalle de capture
    while True:
        try:
            interval_input = input(f"{Fore.CYAN}Enter interval between captures (seconds, default 10) : {Style.RESET_ALL}").strip()
            if not interval_input:
                interval = 10
                break
            interval = int(interval_input)
            if interval < 1:
                print(f"{Fore.RED}[!] Interval must be at least 1 second.{Style.RESET_ALL}")
                continue
            break
        except ValueError:
            print(f"{Fore.RED}[!] Please enter a valid number.{Style.RESET_ALL}")
        except (KeyboardInterrupt, EOFError):
            print(f"\n{Fore.RED}[*] Operation cancelled.{Style.RESET_ALL}")
            return

    # 3. Nom du bot
    try:
        use_default = input(f"{Fore.WHITE}Do you want to keep 'Nexora Logger' as bot name? (y/n, default y) : {Style.RESET_ALL}").strip().lower()
        if use_default in ('n', 'no'):
            username = input(f"{Fore.CYAN}Enter custom bot name : {Style.RESET_ALL}").strip() or "Nexora Logger"
        else:
            username = "Nexora Logger"
    except (KeyboardInterrupt, EOFError):
        print(f"\n{Fore.RED}[*] Operation cancelled.{Style.RESET_ALL}")
        return

    # Sauvegarde sécurisée dans config.json (pas d'injection de code !)
    config_data = {
        "webhook_url": webhook,
        "interval": interval,
        "username": username,
        "message": "Nexora Tool - Monitoring Active"
    }

    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=4)

    print(f"\n{Fore.GREEN}[+] Configuration saved securely to '{config_path}'!{Style.RESET_ALL}")

    # Demander le lancement immédiat
    try:
        launch_now = input(f"\n{Fore.CYAN}Do you want to launch Nexora Logger now? (y/n, default y) : {Style.RESET_ALL}").strip().lower()
        if launch_now in ('', 'y', 'yes'):
            print(f"\n{Fore.GREEN}[*] Launching Nexora Logger...{Style.RESET_ALL}\n")
            # Exécution de combined_logger.py
            import combined_logger
            combined_logger.main()
        else:
            print(f"\n{Fore.YELLOW}[*] You can launch Nexora anytime using:{Style.RESET_ALL}")
            print(f"    python combined_logger.py")
            print(f"    or ./run_nexora.sh (Linux/macOS) / run_nexora.bat (Windows)")
    except (KeyboardInterrupt, EOFError):
        print(f"\n{Fore.YELLOW}[*] Exiting.{Style.RESET_ALL}")

if __name__ == "__main__":
    setup_nexora()
