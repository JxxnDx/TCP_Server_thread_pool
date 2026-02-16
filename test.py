import socket

def test_tcp_server(message, host='localhost', port=5050):
    """
    Cliente de prueba para el servidor TCP.
    
    Args:
        message (str): Mensaje a enviar
        host (str): Host del servidor
        port (int): Puerto del servidor
    """
    try:
        # Crear socket TCP
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Conectar al servidor
        client_socket.connect((host, port))
        print(f"Conectado a {host}:{port}")
        
        # Enviar mensaje
        print(f"Enviando: '{message}'")
        client_socket.sendall(message.encode('utf-8'))
        
        # Recibir respuesta
        response = client_socket.recv(1024).decode('utf-8').strip()
        print(f"Respuesta: {response}")
        
        # Cerrar conexión
        client_socket.close()
        
        return response
        
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    # Casos de prueba
    test_cases = [
        "hola",           # última letra 'a' aparece 1 vez
        "banana",         # última letra 'a' aparece 3 veces
        "reconocer",      # última letra 'r' aparece 3 veces
        "abcdefg",        # última letra 'g' aparece 1 vez
        "aaa",            # última letra 'a' aparece 3 veces
        "test123",        # debe fallar (contiene números)
        "hello world",    # debe fallar (contiene espacio)
    ]
    
    print("=== Pruebas del servidor TCP ===\n")
    
    for test in test_cases:
        print(f"\n--- Prueba con: '{test}' ---")
        test_tcp_server(test)
        print("-" * 40)