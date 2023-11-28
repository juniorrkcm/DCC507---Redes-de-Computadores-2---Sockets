import socket
import threading

# Dicionário para armazenar os clientes conectados, mapeando nomes de usuário para (socket, endereço) correspondentes
clientes = {}

# Função para lidar com um cliente individual
def handle_client(client_socket, addr):
    # Variável para armazenar o nome de usuário do cliente
    username = None
    while True:
        try:
            # Recebe dados do cliente
            data = client_socket.recv(1024).decode('utf-8')
            # Verifica se a conexão foi encerrada
            if not data:
                print(f"Conexão encerrada por {addr}")
                # Remove o cliente da lista se tiver um nome de usuário
                if username:
                    del clientes[username]
                break

            # Verifica se a mensagem é um pedido para definir um nome de usuário
            if data.startswith('/username'):
                # Divide a mensagem para obter o nome de usuário
                _, username = data.split(' ')
                # Adiciona o cliente ao dicionário de clientes
                clientes[username] = (client_socket, addr)
                print(f"Novo usuário registrado: {username}")
            # Verifica se a mensagem é um pedido para listar os usuários conectados
            elif data == '/list':
                # Envia a lista de usuários para o cliente
                client_socket.send(str(clientes.keys()).encode('utf-8'))
            # Verifica se a mensagem é um pedido para iniciar um chat com um usuário específico
            elif data.startswith('/start'):
                _, to_user = data.split(' ')
                to_user = to_user.strip()
                # Verifica se o destinatário está na lista de clientes
                if to_user in clientes:
                    # Envia uma mensagem indicando que o chat está iniciando
                    client_socket.send(f"Conectado a {to_user}".encode('utf-8'))
                    # Inicia o chat entre o remetente e o destinatário
                    start_chat(username, to_user)
                else:
                    # Informa que o destinatário não foi encontrado
                    client_socket.send(f"{to_user} não encontrado".encode('utf-8'))
            else:
                # Imprime a mensagem recebida no servidor
                print(f"Recebido de {username}: {data}")
                # Envia a mensagem para todos os outros clientes
                send_direct_message(username, data)
        except ConnectionResetError:
            # Trata erros de conexão e remove o cliente da lista se tiver um nome de usuário
            print(f"Conexão encerrada por {addr}")
            if username:
                del clientes[username]
            break

# Função para enviar uma mensagem direta a todos os clientes, exceto o remetente
def send_direct_message(sender, message):
    for username, (client_socket, _) in clientes.items():
        if username == sender:
            continue
        try:
            # Envia a mensagem diretamente para cada cliente
            client_socket.send(f"Mensagem de {sender}: {message}".encode('utf-8'))
        except ConnectionResetError:
            print(f"Erro ao enviar mensagem para {username}")

# Função para iniciar um chat entre o remetente e o destinatário
def start_chat(sender, receiver):
    sender_socket, _ = clientes[sender]
    receiver_socket, _ = clientes[receiver]

    # Envia mensagens indicando o início do chat para o remetente e o destinatário
    sender_socket.send(f"Iniciando chat com {receiver}".encode('utf-8'))
    receiver_socket.send(f"Iniciando chat com {sender}".encode('utf-8'))

# Função principal para iniciar o servidor
def start_server():
    # Cria um socket do servidor usando IPv4 e TCP
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Liga o servidor ao endereço 0.0.0.0 (qualquer interface de rede) na porta 8888
    server.bind(('0.0.0.0', 8888))
    # Define o servidor para escutar até 5 conexões pendentes
    server.listen(5)

    print("Servidor escutando na porta 8888...")

    # Loop principal para aceitar clientes e iniciar uma thread para cada um
    while True:
        # Aceita uma conexão do cliente e obtém o socket do cliente e o endereço
        client_socket, addr = server.accept()
        print(f"Conexão aceita de {addr}")

        # Inicia uma thread para lidar com o cliente
        threading.Thread(target=handle_client, args=(client_socket, addr)).start()

# Verifica se o script está sendo executado como programa principal
if __name__ == "__main__":
    # Chama a função start_server() quando o script é executado
    start_server()
