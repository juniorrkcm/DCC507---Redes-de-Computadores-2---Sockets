import socket
import threading

# Função para receber mensagens do servidor em uma thread separada
def receive_messages(client_socket):
    while True:
        try:
            # Recebe dados do socket e os decodifica de utf-8
            data = client_socket.recv(1024).decode('utf-8')
            # Imprime as mensagens recebidas
            print(data)
        except ConnectionResetError:
            # Em caso de erro de conexão, exibe mensagem e encerra o loop
            print("Conexão perdida com o servidor.")
            break

# Função principal para iniciar o cliente
def start_client():
    # Solicita que o usuário digite um nome de usuário
    username = input("Digite seu nome de usuário: ")

    # Cria um socket para o cliente usando IPv4 e TCP
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Conecta o cliente ao servidor no localhost na porta 8888
    client_socket.connect(('localhost', 8888))

    # Envia o nome de usuário para o servidor codificado em utf-8
    client_socket.send(f'/username {username}'.encode('utf-8'))

    # Inicia uma thread para receber mensagens do servidor
    threading.Thread(target=receive_messages, args=(client_socket,)).start()

    # Loop principal para o cliente enviar mensagens
    while True:
        # Solicita que o usuário digite uma mensagem
        message = input()

        # Verifica se a mensagem inicia com '/start'
        if message.startswith('/start'):
            # Divide a mensagem para obter o nome do destinatário
            _, to_user = message.split(' ')
            to_user = to_user.strip()
            # Envia a mensagem '/start' e o nome do destinatário para o servidor
            client_socket.send(f"/start {to_user}".encode('utf-8'))
        else:
            # Envia a mensagem normal para o servidor
            client_socket.send(message.encode('utf-8'))

# Verifica se o script está sendo executado como programa principal
if __name__ == "__main__":
    # Chama a função start_client() quando o script é executado
    start_client()
