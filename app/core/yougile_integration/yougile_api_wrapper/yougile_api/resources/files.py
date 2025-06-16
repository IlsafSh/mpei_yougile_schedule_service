"""
Ресурс для работы с файлами.
"""
from typing import Dict, Any, BinaryIO, Optional
from .base import BaseResource


class FilesResource(BaseResource):
    """Ресурс для работы с файлами."""
    
    _base_url = '/upload-file'
    
    def upload(self, file_data: BinaryIO, file_name: Optional[str] = None) -> str:
        """
        Загрузить файл.
        
        Args:
            file_data: Данные файла
            file_name: Имя файла
            
        Returns:
            str: URL загруженного файла
        """
        files = {'file': (file_name, file_data) if file_name else file_data}
        
        # Для загрузки файла используем multipart/form-data, поэтому не используем стандартный метод request
        url = f"{self._client.BASE_URL}{self._base_url}"
        
        # Подготовка заголовков
        headers = {}
        
        # Добавляем токен в заголовок Authorization, если он есть
        if self._client.token:
            headers["Authorization"] = f"Bearer {self._client.token}"
            
        response = self._client.session.post(url, files=files, headers=headers)
        response.raise_for_status()
        
        # Возвращаем URL загруженного файла
        return response.text

