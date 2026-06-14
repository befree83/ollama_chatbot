"""
Lógica Principal del Chatbot con Auditoría de Logs
Gestiona la conexión con el servicio local de Ollama y reporta anomalías al archivo log.
"""
import ollama
import logging
from core.conversation import ConversationManager

class OfflineChatbot:
    def __init__(self, model_name: str = "gemma3:1b"):
        self.model_name = model_name
        self.conversation = ConversationManager()

    def check_local_model_availability(self) -> bool:
        """Verifica si el modelo requerido está descargado y disponible localmente."""
        try:
            local_models = ollama.list()
            models = [m.get('model', '') if isinstance(m, dict) else getattr(m, 'model', '') for m in local_models.get('models', [])]
            available = any(self.model_name in m for m in models)
            if available:
                logging.info(f"Verificación de modelo exitosa: {self.model_name} está disponible.")
            else:
                logging.warning(f"El modelo {self.model_name} no se encuentra en el entorno local de Ollama.")
            return available
        except Exception as e:
            logging.critical(f"Incapaz de conectar con el demonio local de Ollama: {str(e)}")
            return False

    def send_message(self, user_text: str) -> str:
        """Envía el historial completo al LLM local y recupera la respuesta registrando la métrica."""
        self.conversation.add_message("user", user_text)
        
        try:
            logging.info(f"Iniciando petición de inferencia al modelo '{self.model_name}'...")
            response = ollama.chat(
                model=self.model_name,
                messages=self.conversation.get_history(),
                keep_alive="3h",  # Mantiene el modelo cargado en la memoria por 3 horas para acelerar respuestas subsecuentes
                options={
                    "temperature": 0.3,
                    "top_p": 0.8
                }
            )
            assistant_response = response['message']['content']
            self.conversation.add_message("assistant", assistant_response)
            logging.info("Inferencia completada con éxito y respuesta guardada.")
            return assistant_response
            
        except Exception as e:
            if self.conversation.history and self.conversation.history[-1]["role"] == "user":
                self.conversation.history.pop()
                self.conversation._save_to_disk()
            error_msg = f"Error en la llamada a Ollama: {str(e)}"
            logging.error(error_msg)
            raise RuntimeError(f"Error del servicio Ollama: Asegúrate de que Ollama se está ejecutando en local. Detalles: {str(e)}")