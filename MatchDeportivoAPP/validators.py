"""
Validadores personalizados de contraseñas para MatchDeportivo.

Este módulo contiene validadores adicionales para reforzar la seguridad
de las contraseñas más allá de los validadores por defecto de Django.
"""
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
import re


class UppercaseValidator:
    """
    Valida que la contraseña contenga al menos una letra mayúscula.
    
    Este validador asegura que las contraseñas tengan mayor complejidad
    al requerir al menos un carácter en mayúscula.
    """
    
    def validate(self, password, user=None):
        """
        Valida la contraseña.
        
        Args:
            password (str): La contraseña a validar
            user: El usuario (opcional, para validaciones contextuales)
            
        Raises:
            ValidationError: Si la contraseña no contiene mayúsculas
        """
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                _("La contraseña debe contener al menos una letra mayúscula."),
                code='password_no_upper',
            )
    
    def get_help_text(self):
        """Retorna texto de ayuda para mostrar al usuario."""
        return _("Tu contraseña debe contener al menos una letra mayúscula (A-Z).")


class NumberValidator:
    """
    Valida que la contraseña contenga al menos un número.
    
    Este validador asegura que las contraseñas incluyan caracteres numéricos
    para aumentar la complejidad y dificultar ataques de fuerza bruta.
    """
    
    def validate(self, password, user=None):
        """
        Valida la contraseña.
        
        Args:
            password (str): La contraseña a validar
            user: El usuario (opcional, para validaciones contextuales)
            
        Raises:
            ValidationError: Si la contraseña no contiene números
        """
        if not re.search(r'[0-9]', password):
            raise ValidationError(
                _("La contraseña debe contener al menos un número."),
                code='password_no_number',
            )
    
    def get_help_text(self):
        """Retorna texto de ayuda para mostrar al usuario."""
        return _("Tu contraseña debe contener al menos un número (0-9).")


class SpecialCharacterValidator:
    """
    Valida que la contraseña contenga al menos un carácter especial.
    
    Los caracteres especiales incluyen: !@#$%^&*()_+-=[]{}|;:,.<>?
    Esto añade una capa adicional de seguridad a las contraseñas.
    """
    
    def validate(self, password, user=None):
        """
        Valida la contraseña.
        
        Args:
            password (str): La contraseña a validar
            user: El usuario (opcional, para validaciones contextuales)
            
        Raises:
            ValidationError: Si la contraseña no contiene caracteres especiales
        """
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password):
            raise ValidationError(
                _("La contraseña debe contener al menos un carácter especial (!@#$%^&*...)."),
                code='password_no_special',
            )
    
    def get_help_text(self):
        """Retorna texto de ayuda para mostrar al usuario."""
        return _("Tu contraseña debe contener al menos un carácter especial (!@#$%^&*...).")
