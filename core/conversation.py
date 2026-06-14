"""
Gestión del Historial de Conversación con Persistencia Local y Logs
Maneja la preservación del contexto en archivos JSON y registra eventos de auditoría.
"""
import os
import json
import logging

# Configuración del sistema de logs del lado del servidor/core
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class ConversationManager:
    def __init__(self, storage_path: str = "storage/chat_history.json"):
        self.history = []
        self.active_expert_id = None
        self.storage_path = storage_path
        
        # Asegurar que el directorio de almacenamiento existe
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)

    def _save_to_disk(self):
        """Guarda de forma persistente el historial actual en un archivo JSON."""
        try:
            # Intentar cargar datos existentes para no machacar otros expertos
            data = {}
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        data = {}

            # Actualizar solo el contexto del experto activo
            if self.active_expert_id:
                data[self.active_expert_id] = self.history
                
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logging.error(f"No se pudo persistir el historial en disco: {str(e)}")

    def _load_from_disk(self, expert_id: str) -> list:
        """Carga el historial guardado en disco para un experto específico."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get(expert_id, [])
            except Exception as e:
                logging.error(f"Error al leer el historial desde el disco: {str(e)}")
        return []

    def initialize_expert(self, expert_id: str, system_prompt: str):
        """Define el experto, recupera su historial del disco o inyecta el prompt inicial."""
        self.active_expert_id = expert_id
        saved_history = self._load_from_disk(expert_id)

        if saved_history:
            self.history = saved_history
            logging.info(f"Historial persistente recuperado para el experto ID: {expert_id}")
        else:
            self.history = [{"role": "system", "content": system_prompt}]
            self._save_to_disk()
            logging.info(f"Nuevo contexto inicializado para el experto ID: {expert_id}")

    def add_message(self, role: str, content: str):
        """Añade un mensaje al historial y lo vuelca inmediatamente a disco."""
        self.history.append({"role": role, "content": content})
        self._save_to_disk()
        logging.info(f"Mensaje registrado en el historial. Rol: {role}")

    def get_history(self):
        """Devuelve el historial completo del contexto."""
        return self.history

    def clear_history(self):
        """Reinicia el historial manteniendo únicamente el prompt de sistema inicial."""
        if self.history:
            system_msg = self.history[0]
            self.history = [system_msg]
        else:
            self.history = []
        self._save_to_disk()
        logging.info(f"Historial limpiado explícitamente para el experto ID: {self.active_expert_id}")