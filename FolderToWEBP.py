import os
import subprocess
import argparse
import glob
import platform
import urllib.request
import tarfile
import zipfile

# Создаем парсер аргументов
parser = argparse.ArgumentParser(description='Конвертирует все изображения .jpg, .jpeg и .png в указанной директории в формат .webp.')
parser.add_argument('--compress', type=int, default=80, help='Уровень качества сжатия (по умолчанию: 80)')
parser.add_argument('--source', type=str, default='.', help='Директория с исходными изображениями (по умолчанию: текущая директория)')
parser.add_argument('--output', type=str, default=None, help='Директория для сохранения конвертированных изображений (по умолчанию: поддиректория "converted_images" в директории исходных изображений)')
parser.add_argument('--force', action='store_true', help='Перезаписывает существующие файлы .webp')

# Парсим аргументы командной строки
args = parser.parse_args()

# Устанавливаем качество сжатия и директории по умолчанию, если они не указаны в аргументах командной строки
quality = args.compress
source_dir = args.source
output_dir = args.output if args.output else os.path.join(source_dir, 'converted_images')
force = args.force

# Создаем выходную директорию, если она еще не существует
os.makedirs(output_dir, exist_ok=True)

# Проверяем, установлен ли cwebp
if not subprocess.run(['which', 'cwebp'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
    print("cwebp не установлен. Устанавливаем cwebp...")
    # Определяем операционную систему
    os_name = platform.system()
    if os_name == "Linux":
        # Устанавливаем cwebp на Linux
        if platform.machine() == "aarch64":
            url = "https://storage.googleapis.com/downloads.webmproject.org/releases/webp/libwebp-1.3.2-linux-aarch64.tar.gz"
        else:
            url = "https://storage.googleapis.com/downloads.webmproject.org/releases/webp/libwebp-1.3.2-linux-x86-64.tar.gz"
        file_tmp = "/tmp/libwebp.tar.gz"
        dir_tmp = "/tmp/libwebp"
        urllib.request.urlretrieve(url, file_tmp)
        with tarfile.open(file_tmp, 'r:gz') as tar:
            tar.extractall(path=dir_tmp)
        os.rename(os.path.join(dir_tmp, "libwebp-1.3.2-linux-x86-64", "bin", "cwebp"), "/usr/local/bin/cwebp")
    elif os_name == "Darwin":
        # Устанавливаем cwebp на macOS
        if subprocess.run(['which', 'brew'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
            # Если установлен Homebrew, устанавливаем cwebp через Homebrew
            subprocess.run(['brew', 'install', 'webp'], check=True)
        else:
            # Если Homebrew не установлен, устанавливаем cwebp из файла с сайта
            if platform.machine() == "arm64":
                url = "https://storage.googleapis.com/downloads.webmproject.org/releases/webp/libwebp-1.3.2-mac-arm64.tar.gz"
            else:
                url = "https://storage.googleapis.com/downloads.webmproject.org/releases/webp/libwebp-1.3.2-mac-x86-64.tar.gz"
            file_tmp = "/tmp/libwebp.tar.gz"
            dir_tmp = "/tmp/libwebp"
            urllib.request.urlretrieve(url, file_tmp)
            with tarfile.open(file_tmp, 'r:gz') as tar:
                tar.extractall(path=dir_tmp)
            os.rename(os.path.join(dir_tmp, "libwebp-1.3.2-mac-x86-64", "bin", "cwebp"), "/usr/local/bin/cwebp")
    elif os_name == "Windows":
        # Устанавливаем cwebp на Windows
        url = "https://storage.googleapis.com/downloads.webmproject.org/releases/webp/libwebp-1.3.2-windows-x64.zip"
        file_tmp = "C:\\Temp\\libwebp.zip"
        dir_tmp = "C:\\Temp\\libwebp"
        urllib.request.urlretrieve(url, file_tmp)
        with zipfile.ZipFile(file_tmp, 'r') as zip_ref:
            zip_ref.extractall(dir_tmp)
        os.rename(os.path.join(dir_tmp, "libwebp-1.3.2-windows-x64", "bin", "cwebp.exe"), "C:\\Windows\\System32\\cwebp.exe")
    else:
        print("Не удалось определить операционную систему или ваша операционная система не поддерживается.")
        sys.exit(1)
    print("Установка cwebp завершена.")

# Выводим заголовок таблицы
print("| %-30s | %-15s | %-15s | %-10s | %-10s |" % ("Имя файла", "Старый размер", "Новый размер", "Экономия", "Статус"))
print("| %-30s | %-15s | %-15s | %-10s | %-10s |" % ("------------------------------", "---------------", "---------------", "----------", "----------"))

# Перебираем все файлы с расширением .jpg, .jpeg и .png в указанной директории
for ext in ['jpg', 'jpeg', 'png']:
    for file in glob.glob(os.path.join(source_dir, '*.' + ext)):
        # Получаем имя файла без расширения
        filename = os.path.basename(file)
        extension = os.path.splitext(filename)[1]
        filename = os.path.splitext(filename)[0]

        # Проверяем, существует ли уже файл .webp
        if not os.path.exists(os.path.join(output_dir, filename + '.webp')) or force:
            # Если файла .webp не существует или установлен флаг --force, конвертируем файл в webp с помощью cwebp
            result = subprocess.run(['cwebp', '-q', str(quality), file, '-o', os.path.join(output_dir, filename + '.webp')], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if result.returncode == 0:
                old_size = os.path.getsize(file) // 1024
                new_size = os.path.getsize(os.path.join(output_dir, filename + '.webp')) // 1024
                saved_space = old_size - new_size
                status = "Успешно"
            else:
                old_size = "N/A"
                new_size = "N/A"
                saved_space = "N/A"
                status = "Ошибка"
        else:
            old_size = "N/A"
            new_size = "N/A"
            saved_space = "N/A"
            status = "Уже существует"

        # Выводим строку таблицы
        print("| %-30s | %-15s | %-15s | %-10s | %-10s |" % (file, str(old_size) + " KB", str(new_size) + " KB", str(saved_space) + " KB", status))
