import socket
import threading
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class TCPServer:
    def __init__(self, host='0.0.0.0', port=5050):
        self.host = host
        self.port = port
        self.server_socket = None
        
    def count_last_character(self, text):
        """
        Cuenta cuántas veces aparece el último carácter en la cadena de texto.
        
        Args:
            text (str): Cadena de texto a analizar
            
        Returns:
            int: Número de veces que aparece el último carácter
        """
        if not text:
            return 0
        
        last_char = text[-1].lower()
        count = sum(1 for char in text.lower() if char == last_char)
        return count
    
    def validate_text(self, text):
        """
        Valida que el texto solo contenga caracteres alfabéticos.
        
        Args:
            text (str): Cadena de texto a validar
            
        Returns:
            bool: True si es válido, False en caso contrario
        """
        return text.isalpha()
    
    def handle_client(self, client_socket, client_address):
        """
        Maneja la conexión de un cliente.
        
        Args:
            client_socket: Socket del cliente
            client_address: Dirección del cliente
        """
        logging.info(f"Nueva conexión desde {client_address}")
        
        try:
            # Recibir datos del cliente
            data = client_socket.recv(1024).decode('utf-8').strip()
            
            if not data:
                logging.warning(f"Datos vacíos recibidos de {client_address}")
                client_socket.sendall(b"ERROR: No se recibieron datos\n")
                return
            
            logging.info(f"Mensaje recibido de {client_address}: '{data}'")
            
            # Validar que solo contenga caracteres alfabéticos
            if not self.validate_text(data):
                error_msg = "ERROR: El mensaje debe contener solo caracteres alfabéticos\n"
                logging.warning(f"Validación fallida para {client_address}: '{data}'")
                client_socket.sendall(error_msg.encode('utf-8'))
                return
            
            # Contar las apariciones del último carácter
            count = self.count_last_character(data)
            
            # Enviar respuesta al cliente
            response = f"{count}\n"
            client_socket.sendall(response.encode('utf-8'))
            
            logging.info(f"Respuesta enviada a {client_address}: {count} (último carácter: '{data[-1]}')")
            
        except Exception as e:
            logging.error(f"Error manejando cliente {client_address}: {e}")
            try:
                client_socket.sendall(b"ERROR: Error interno del servidor\n")
            except:
                pass
        finally:
            client_socket.close()
            logging.info(f"Conexión cerrada con {client_address}")
    
    def start(self):
        """
        Inicia el servidor TCP.
        """
        try:
            # Crear socket TCP
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Vincular al host y puerto
            self.server_socket.bind((self.host, self.port))
            
            # Escuchar conexiones (backlog de 100 conexiones pendientes)
            self.server_socket.listen(100)
            
            logging.info(f"Servidor TCP iniciado en {self.host}:{self.port}")
            logging.info("Esperando conexiones...")
            
            while True:
                # Aceptar conexión del cliente
                client_socket, client_address = self.server_socket.accept()
                
                # Crear un thread para manejar el cliente
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, client_address)
                )
                client_thread.daemon = True
                client_thread.start()
                
        except KeyboardInterrupt:
            logging.info("\nDeteniendo servidor...")
        except Exception as e:
            logging.error(f"Error en el servidor: {e}")
        finally:
            if self.server_socket:
                self.server_socket.close()
                logging.info("Servidor cerrado")

if __name__ == "__main__":
    server = TCPServer(host='0.0.0.0', port=5050)
    server.start()