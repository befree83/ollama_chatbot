"""
Punto de Entrada de la Aplicación con Logs del Sistema
Maneja la UI en consola y registra los accesos o cierres de sesión.
"""
import sys
import logging
from core.chatbot import OfflineChatbot
from experts.expert_prompts import EXPERT_PROMPTS

def display_menu():
    print("\n" + "="*50)
    print("  CHATBOT MULTI-EXPERTO LOCAL (Gemma3:1b)")
    print("="*50)
    print("Selecciona un experto para conversar:")
    for key, expert in EXPERT_PROMPTS.items():
        # Informar al usuario si ya cuenta con historial guardado previamente
        print(f" [{key}] {expert['name']}")
    print(" [E] Salir de la aplicación")
    print("="*50)

def display_chat_commands():
    print("\n--- Comandos: /change (Cambiar Experto) | /reset (Reiniciar Historial) | /exit (Salir) ---")

def main():
    chatbot = OfflineChatbot(model_name="gemma3:1b")
    
    print("[Sistema] Verificando el entorno local y el servicio Ollama...")
    if not chatbot.check_local_model_availability():
        print(f"[ERROR] El modelo '{chatbot.model_name}' no se encontró o el servicio Ollama es inaccesible.")
        print("Por favor, ejecuta 'ollama run gemma3:1b' en tu terminal antes de iniciar esta aplicación.")
        sys.exit(1)
    
    print("[Éxito] Entorno verificado. Funcionando completamente offline.")
    logging.info("Aplicación iniciada correctamente por el usuario.")

    while True:
        display_menu()
        choice = input("Selecciona una opción: ").strip().lower()

        if choice == 'e':
            print("\nCerrando la aplicación. ¡Hasta luego!")
            logging.info("Aplicación finalizada por comando de salida de usuario.")
            break
            
        if choice in EXPERT_PROMPTS:
            selected_expert = EXPERT_PROMPTS[choice]
            chatbot.conversation.initialize_expert(choice, selected_expert["system_prompt"])
            
            print(f"\n[Sistema] Conectado con: **{selected_expert['name']}**")
            print(f"[Sistema] Sincronizando el historial persistente desde el disco...")
            display_chat_commands()

            while True:
                user_input = input("\nTú: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() == '/exit':
                    print("\nCerrando la aplicación. ¡Hasta luego!")
                    logging.info("Aplicación finalizada desde la sesión de chat.")
                    sys.exit(0)
                    
                elif user_input.lower() == '/change':
                    print("\n[Sistema] Guardando sesión y cambiando de experto...")
                    logging.info("El usuario cambió de experto temático.")
                    break
                    
                elif user_input.lower() == '/reset':
                    chatbot.conversation.clear_history()
                    print(f"\n[Sistema] Historial borrado en disco para {selected_expert['name']}. Conversación reiniciada.")
                    continue
                
                try:
                    print(f"\n[{selected_expert['name']}] Pensando...")
                    reply = chatbot.send_message(user_input)
                    print(f"\n[{selected_expert['name']}]: {reply}")
                except Exception as error:
                    print(f"\n[ERROR CRÍTICO] {str(error)}")
        else:
            print("\n[Opción Inválida] Por favor, selecciona un índice válido del menú.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSesión interrumpida por el usuario. Saliendo de forma segura.")
        logging.warning("La aplicación se cerró abruptamente por KeyboardInterrupt.")
        sys.exit(0)