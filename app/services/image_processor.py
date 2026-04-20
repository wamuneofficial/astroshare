"""
Обработка загружаемых изображений:
- Проверка что файл действительно является изображением
- Создание превью 400x400 для JPG/PNG/TIFF
"""

import os
import uuid
from PIL import Image, UnidentifiedImageError


# Разрешённые расширения файлов
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'tiff', 'tif'}

# Размер превью
THUMBNAIL_SIZE = (400, 400)


def get_extension(filename):
    """Возвращает расширение файла в нижнем регистре, без точки."""
    if '.' not in filename:
        return ''
    return filename.rsplit('.', 1)[-1].lower()


def is_allowed(filename):
    """Проверяет, разрешено ли расширение файла."""
    return get_extension(filename) in ALLOWED_EXTENSIONS


def validate_image(file_path):
    """
    Проверяет что файл действительно является изображением,
    открывая его через Pillow. Защита от загрузки файлов с
    поддельным расширением (например, script.php переименованный в photo.jpg).
    Возвращает True если файл валиден, False если нет.
    """
    try:
        with Image.open(file_path) as img:
            img.verify()  # verify() проверяет структуру файла без полного декодирования
        return True
    except (UnidentifiedImageError, Exception):
        return False


def create_thumbnail(source_path, upload_folder):
    """
    Создаёт уменьшенную копию изображения 400x400.
    Возвращает имя файла превью (UUID.jpg) или None если не получилось.
    """
    try:
        with Image.open(source_path) as img:
            # thumbnail() уменьшает изображение вписывая в размер, сохраняя пропорции
            img.thumbnail(THUMBNAIL_SIZE, Image.LANCZOS)

            # JPEG не поддерживает прозрачность — конвертируем RGBA и P в RGB
            if img.mode in ('RGBA', 'P', 'LA'):
                background = Image.new('RGB', img.size, (10, 10, 30))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background

            thumb_filename = f'thumb_{uuid.uuid4().hex}.jpg'
            thumb_path = os.path.join(upload_folder, thumb_filename)
            img.save(thumb_path, 'JPEG', quality=85, optimize=True)
            return thumb_filename

    except Exception:
        # Если не удалось создать превью — не падаем, просто возвращаем None
        return None


def process_upload(file_object, upload_folder):
    """
    Основная функция обработки загруженного файла.

    Принимает:
        file_object   — FileStorage объект из формы (form.photo.data)
        upload_folder — путь к папке uploads/

    Возвращает словарь:
        {
            'filename':      'uuid.jpg',       # имя сохранённого файла
            'thumbnail':     'thumb_uuid.jpg', # имя превью (или None)
            'file_format':   'JPG',            # формат в верхнем регистре
            'error':         None              # текст ошибки или None
        }
    """
    original_name = file_object.filename

    if not is_allowed(original_name):
        return {'error': 'format_not_allowed'}

    ext = get_extension(original_name)
    new_filename = f'{uuid.uuid4().hex}.{ext}'
    save_path = os.path.join(upload_folder, new_filename)

    # Сохраняем оригинал
    file_object.save(save_path)

    # Проверяем что это действительно изображение (не исполняемый файл)
    if not validate_image(save_path):
        os.remove(save_path)
        return {'error': 'not_an_image'}

    # Создаём превью для растровых форматов
    thumbnail_filename = None
    if ext in ('jpg', 'jpeg', 'png', 'tiff', 'tif'):
        thumbnail_filename = create_thumbnail(save_path, upload_folder)

    return {
        'filename': new_filename,
        'thumbnail': thumbnail_filename,
        'file_format': ext.upper().replace('JPEG', 'JPG'),
        'error': None,
    }
