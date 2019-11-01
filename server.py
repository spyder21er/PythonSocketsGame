import socket
import select
import sys
import os
import pickle
import time


def clear_scr():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_welcome():
    height = len(welcome_text)
    for i in range(height):
        clear_scr()
        lines = height - i
        while lines:
            print()
            lines -= 1
        for j in range(i+1):
            print(welcome_text[j])
        time.sleep(0.1)


def new_game():
    return [7, 3, 5, 9, 1, 7]


def print_game(game):
    clear_scr()
    letters = ["A: ", "B: ", "C: ", "D: ", "E: ", "F: ", "G: ", "H: ", "I: ", "J: "]
    # ╔╗
    # ╚╝

    for i in range(len(game)):
        print(letters[i], end="")
        col = game[i]
        while col:
            print("╔╗ ", end="")
            col -= 1
        print("\n   ", end="")
        col = game[i]
        while col:
            print("╚╝ ", end="")
            col -= 1
        print()


def send_game_status(client_socket, game):
    game_status = pickle.dumps(game)
    game_status = bytes(f"{len(game_status):<{HEADER_LENGTH}}", "utf-8") + game_status
    client_socket.send(game_status)


def send_to_client(client_socket, my_command):
    my_command = f"{len(my_command):<{HEADER_LENGTH}}".encode("utf-8") + my_command.encode("utf-8")
    try:
        client_socket.send(my_command)
    except:
        print("Client disconnected")
        client_socket.close()
        sys.exit(1)

        
def get_client_move(client_socket):
    header = client_socket.recv(HEADER_LENGTH)
    if not header:
        print("Client disconnected")
        client_socket.close()
        sys.exit(1)
    opponent_move_length = int(header.decode("utf-8"))
    return client_socket.recv(opponent_move_length).decode("utf-8")


def valid_move(command, game):

    # check if it is 2 char
    if len(command) != 2:
        return False

    # check if first char is number
    if not command[0].isdigit():
        return False

    # check if second char is letter
    if not command[1].isalpha():
        return False

    # check if letter is within range
    row = ord(command[1].lower()) - ord('a')
    if row >= len(game):
        return False

    # check if there is enough number of cards
    if int(command[0]) > game[row]:
        return False
    
    return True

 
def change_status(game, command):
    row = int(ord(command[1].lower()) - ord('a'))
    game[row] -= int(command[0])
    return game

HEADER_LENGTH = 10
IP = "127.0.0.1"
PORT = 8878

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((IP, PORT))
server_socket.listen(1)
clear_scr()

welcome_text = [
    "+============================================================================================+",
    "|    ██╗    ██╗███████╗██╗      ██████╗ ██████╗ ███╗   ███╗███████╗    ████████╗ ██████╗     |",
    "|    ██║    ██║██╔════╝██║     ██╔════╝██╔═══██╗████╗ ████║██╔════╝    ╚══██╔══╝██╔═══██╗    |",
    "|    ██║ █╗ ██║█████╗  ██║     ██║     ██║   ██║██╔████╔██║█████╗         ██║   ██║   ██║    |",
    "|    ██║███╗██║██╔══╝  ██║     ██║     ██║   ██║██║╚██╔╝██║██╔══╝         ██║   ██║   ██║    |",
    "|    ╚███╔███╔╝███████╗███████╗╚██████╗╚██████╔╝██║ ╚═╝ ██║███████╗       ██║   ╚██████╔╝    |",
    "|     ╚══╝╚══╝ ╚══════╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝       ╚═╝    ╚═════╝     |",
    "|                                                                                            |",
    "|         ███╗   ██╗██╗███╗   ███╗███████╗     ██████╗  █████╗ ███╗   ███╗███████╗           |",
    "|         ████╗  ██║██║████╗ ████║██╔════╝    ██╔════╝ ██╔══██╗████╗ ████║██╔════╝           |",
    "|         ██╔██╗ ██║██║██╔████╔██║███████╗    ██║  ███╗███████║██╔████╔██║█████╗             |",
    "|         ██║╚██╗██║██║██║╚██╔╝██║╚════██║    ██║   ██║██╔══██║██║╚██╔╝██║██╔══╝             |",
    "|         ██║ ╚████║██║██║ ╚═╝ ██║███████║    ╚██████╔╝██║  ██║██║ ╚═╝ ██║███████╗           |",
    "|         ╚═╝  ╚═══╝╚═╝╚═╝     ╚═╝╚══════╝     ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝           |",
    "+============================================================================================+",
    "|   Instructions:                                                                            |",
    "|   1. Cards are laid out in rows                                                            |",
    "|   2. Each player take turns taking cards                                                   |",
    "|   3. Players can take any number of cards in any row but only from one row at a time       |",
    "|   4. The player who takes the last card loses the game                                     |",
    "|   5. To take cards, type NR where N is the number of cards and R is the row letter.        |",
    "|   6. For example the command '3B' will take 3 cards from row B                             |",
    "+============================================================================================+"
]

print("Waiting for opponent...")
client_socket, client_address = server_socket.accept()
# after making connection we wil print the intro
print_welcome()

while True:
    command = input("Enter 's' to start or 'q' to quit: ")
    if (command == 's' or command == 'q'):
        break

if command == 'q':
    sys.exit()

#create new game
game = new_game()
your_turn = False
opponent_move = False
game_won = False
game_ended = False

while not game_ended:
    # send the game status to client
    print_game(game)
    if opponent_move:
        print(f"Opponent's last move: {opponent_move}")
        opponent_move = False

    try:
        send_game_status(client_socket, game)
    except:
        print("Client disconnected")
        client_socket.close()
        sys.exit(1)
    
    if your_turn:
        # get a valid command from input
        while True:
            command = input("Take cards <NoOfCards><RowLetter> or 'q' to quit: ")
            if valid_move(command, game) or command == 'q':
                break

        # quit if q
        if (command == 'q'):
            print("You disconnected.")
            sys.exit()
        
        # update the game
        game = change_status(game, command)
        send_to_client(client_socket, command)
        game_ended = all(i == 0 for i in game)
        game_won = False
    else:
        print("Waiting for your opponent to take cards...")
        opponent_move = get_client_move(client_socket)
        game = change_status(game, opponent_move)
        game_ended = all(i == 0 for i in game)
        game_won = True

    
    your_turn = not your_turn

try:
    send_game_status(client_socket, game)
except:
    print("Client disconnected")
    client_socket.close()
    sys.exit(1)

if game_won:
    print_game(game)
    print(f"Opponent's last move: {opponent_move}")
    print("Congratulations! You won the game!")
else:
    print("Sorry you lose. :(")

client_socket.close()
