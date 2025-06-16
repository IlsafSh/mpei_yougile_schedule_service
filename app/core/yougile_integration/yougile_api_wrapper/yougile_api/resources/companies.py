"""
Ресурс для работы с компаниями.
"""
from typing import Dict, Any, List, Optional
from .base import BaseResource, CRUDResourceMixin


class CompaniesResource(BaseResource, CRUDResourceMixin):
    """Ресурс для работы с компаниями."""
    
    _base_url = '/companies'
    
    def get(self, id: str) -> Dict[str, Any]:
        """
        Получить компанию по ID.
        
        Args:
            id: ID компании
            
        Returns:
            dict: Компания
        """
        return super().get(id)
    
    def update(self, id: str, title: Optional[str] = None) -> Dict[str, Any]:
        """
        Обновить компанию.
        
        Args:
            id: ID компании
            title: Название компании
            
        Returns:
            dict: Обновленная компания
        """
        data = {}
        
        if title is not None:
            data['title'] = title
            
        return super().update(id, **data)

