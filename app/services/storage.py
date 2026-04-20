"""
Абстракция хранилища файлов.

Сейчас используем LocalStorage — сохраняем файлы в папку uploads/.
В будущем достаточно написать класс S3Storage с теми же методами
и заменить одну строку в get_storage() — всё остальное не изменится.
"""

import os
from flask import current_app, url_for


class LocalStorage:
    """Хранит файлы локально в папке uploads/."""

    def save(self, file_object, filename):
        """
        Сохраняет файл на диск.
        file_object — объект FileStorage от Flask (form.photo.data).
        filename — уже готовое имя файла (UUID + расширение).
        """
        path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file_object.save(path)
        return path

    def save_from_path(self, src_path, filename):
        """Сохраняет уже существующий файл под новым именем (для превью)."""
        dst_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        import shutil
        shutil.copy2(src_path, dst_path)
        return dst_path

    def get_url(self, filename):
        """Возвращает URL для доступа к файлу через браузер."""
        if not filename:
            return None
        return url_for('main.uploaded_file', filename=filename)

    def delete(self, filename):
        """Удаляет файл с диска. Молча игнорирует если файла нет."""
        if not filename:
            return
        path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(path):
            os.remove(path)

    def get_path(self, filename):
        """Возвращает полный путь к файлу на диске."""
        return os.path.join(current_app.config['UPLOAD_FOLDER'], filename)


# Единственный экземпляр хранилища — импортируй его везде где нужно.
# Чтобы переключиться на S3, замени LocalStorage() на S3Storage() здесь.
storage = LocalStorage()
