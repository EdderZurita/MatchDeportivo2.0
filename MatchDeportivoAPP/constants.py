"""Constantes del proyecto."""

# Deportes disponibles
DEPORTES = [
    ('futbol', 'Fútbol'),
    ('basketball', 'Basketball'),
    ('skate', 'Skate'),
    ('volibol', 'Vólibol'),
    ('running', 'Running'),
    ('tenis', 'Tenis'),
]

# Niveles de habilidad
NIVELES = [
    ('Principiante', 'Principiante'),
    ('Intermedio', 'Intermedio'),
    ('Avanzado', 'Avanzado'),
]

# Iconos de perfil disponibles
ICONOS_PERFIL = [
    {'value': 'futbol', 'path': 'img/futbol.png', 'name': 'Fútbol'},
    {'value': 'basketball', 'path': 'img/basketball.png', 'name': 'Basketball'},
    {'value': 'skate', 'path': 'img/skate.png', 'name': 'Skate'},
    {'value': 'voleibol', 'path': 'img/voleibol.png', 'name': 'Vóleibol'},
    {'value': 'running', 'path': 'img/running.png', 'name': 'Running'},
    {'value': 'tenis', 'path': 'img/tenis.png', 'name': 'Tenis'},
]

# Radio de búsqueda por defecto (km)
RADIO_BUSQUEDA_DEFAULT = 50

# Radio de la Tierra en kilómetros (para cálculos de distancia)
RADIO_TIERRA_KM = 6371
