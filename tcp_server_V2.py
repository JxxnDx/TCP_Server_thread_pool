import socket
import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import threading
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(threadName)s] - %(message)s'
)

class TCPServerEnhanced:
    def __init__(self, host='0.0.0.0', port=5050, max_workers=50, log_file='resultados.txt'):
        self.host = host
        self.port = port
        self.max_workers = max_workers
        self.log_file = log_file
        self.server_socket = None
        self.pool = None
        # Lock para escritura segura en el archivo
        self.file_lock = threading.Lock()
        self.vowels = set('aeiouAEIOU')
        
        # Crear archivo con encabezado si no existe
        self._initialize_log_file()
    
    def _initialize_log_file(self):
        """Inicializa el archivo de log si no existe."""
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("REGISTRO DE MENSAJES TCP - SERVIDOR DE CONTEO DE VOCALES\n")
                f.write("=" * 80 + "\n\n")
            logging.info(f"Archivo de log creado: {self.log_file}")
        else:
            logging.info(f"Usando archivo de log existente: {self.log_file}")
    
    def find_last_vowel(self, text):
        """
        Encuentra la última vocal en el texto.
        
        Args:
            text (str): Texto a analizar
            
        Returns:
            str or None: La última vocal encontrada o None si no hay vocales
        """
        # Recorrer el texto de derecha a izquierda
        for char in reversed(text):
            if char in self.vowels:
                return char.lower()
        return None
    
    def count_vowel_occurrences(self, text, vowel):
        """
        Cuenta cuántas veces aparece una vocal específica en el texto.
        
        Args:
            text (str): Texto a analizar
            vowel (str): Vocal a contar
            
        Returns:
            int: Número de apariciones
        """
        if not vowel:
            return 0
        return sum(1 for char in text.lower() if char == vowel.lower())
    
    def is_prime(self, n):
        """
        Determina si un número es primo.
        
        Args:
            n (int): Número a verificar
            
        Returns:
            bool: True si es primo, False en caso contrario
        """
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        
        # Verificar divisores hasta la raíz cuadrada
        for i in range(3, int(n ** 0.5) + 1, 2):
            if n % i == 0:
                return False
        return True
    
    def validate_text(self, text):
        """
        Valida que el texto solo contenga caracteres alfabéticos y espacios.
        
        Args:
            text (str): Cadena de texto a validar
            
        Returns:
            bool: True si es válido, False en caso contrario
        """
        # Permitir letras y espacios
        return all(char.isalpha() or char.isspace() for char in text)
    
    def save_to_log(self, timestamp, message, count, is_prime_result, last_vowel):
        """
        Guarda el resultado en el archivo de log de manera thread-safe.
        
        Args:
            timestamp (str): Fecha y hora
            message (str): Mensaje recibido
            count (int): Número de veces que se repite la vocal
            is_prime_result (str): "SI" o "NO"
            last_vowel (str): Última vocal encontrada
        """
        with self.file_lock:
            try:
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(f"Fecha: {timestamp}\n")
                    f.write(f"Mensaje: {message}\n")
                    f.write(f"Última vocal: {last_vowel}\n")
                    f.write(f"Repeticiones: {count}\n")
                    f.write(f"¿Es primo?: {is_prime_result}\n")
                    f.write("-" * 80 + "\n\n")
                logging.info(f"Registro guardado en {self.log_file}")
            except Exception as e:
                logging.error(f"Error al guardar en archivo: {e}")
    
    def handle_client(self, client_socket, client_address):
        """Maneja la conexión de un cliente."""
        logging.info(f"Nueva conexión desde {client_address}")
        
        try:
            # Recibir datos (buffer más grande para mensajes largos)
            data = client_socket.recv(4096).decode('utf-8').strip()
            
            if not data:
                logging.warning(f"Datos vacíos recibidos de {client_address}")
                client_socket.sendall(b"ERROR: No se recibieron datos\n")
                return
            
            logging.info(f"Mensaje recibido de {client_address}: '{data}'")
            
            # Validar que solo contenga letras y espacios
            if not self.validate_text(data):
                error_msg = "ERROR: El mensaje debe contener solo letras y espacios\n"
                logging.warning(f"Validación fallida para {client_address}: '{data}'")
                client_socket.sendall(error_msg.encode('utf-8'))
                return
            
            # Verificar que no sea solo espacios
            if not data.strip():
                error_msg = "ERROR: El mensaje no puede estar vacío o contener solo espacios\n"
                logging.warning(f"Mensaje vacío de {client_address}")
                client_socket.sendall(error_msg.encode('utf-8'))
                return
            
            # Buscar la última vocal
            last_vowel = self.find_last_vowel(data)
            
            if not last_vowel:
                error_msg = "ERROR: El mensaje debe contener al menos una vocal\n"
                logging.warning(f"Sin vocales en mensaje de {client_address}")
                client_socket.sendall(error_msg.encode('utf-8'))
                return
            
            # Contar las apariciones de la última vocal
            count = self.count_vowel_occurrences(data, last_vowel)
            
            # Verificar si el número es primo
            is_prime_result = "SI" if self.is_prime(count) else "NO"
            
            # Obtener timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Guardar en archivo
            self.save_to_log(timestamp, data, count, is_prime_result, last_vowel)
            
            # Enviar respuesta al cliente
            response = f"{count}\n"
            client_socket.sendall(response.encode('utf-8'))
            
            logging.info(
                f"Respuesta enviada a {client_address}: {count} "
                f"(vocal: '{last_vowel}', primo: {is_prime_result})"
            )
            
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
        """Inicia el servidor con Thread Pool."""
        try:
            # Crear Thread Pool
            self.pool = ThreadPoolExecutor(
                max_workers=self.max_workers,
                thread_name_prefix="Worker"
            )
            
            # Crear socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(100)
            
            logging.info(f"Servidor TCP iniciado en {self.host}:{self.port}")
            logging.info(f"Thread Pool con {self.max_workers} workers")
            logging.info(f"Guardando resultados en: {self.log_file}")
            logging.info("Esperando conexiones...")
            
            while True:
                # Aceptar conexión
                client_socket, client_address = self.server_socket.accept()
                
                # Enviar tarea al pool
                self.pool.submit(self.handle_client, client_socket, client_address)
                
        except KeyboardInterrupt:
            logging.info("\nDeteniendo servidor...")
        except Exception as e:
            logging.error(f"Error en el servidor: {e}")
        finally:
            if self.pool:
                logging.info("Cerrando Thread Pool...")
                self.pool.shutdown(wait=True)
            if self.server_socket:
                self.server_socket.close()
            logging.info("Servidor cerrado")

if __name__ == "__main__":
    # Crear servidor con pool de 50 threads
    # Los resultados se guardarán en 'resultados.txt'
    server = TCPServerEnhanced(
        host='0.0.0.0',
        port=5050,
        max_workers=50,
        log_file='resultados.txt'
    )
    server.start()