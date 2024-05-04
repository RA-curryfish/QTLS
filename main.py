import sys
import socket
import qhash
import warnings

warnings.filterwarnings("ignore", category=RuntimeWarning)

delim = "::::"
bad_data = "Bad"

class QPacket:
    
    def __init__(self,data):
        self.data = data
        self.QMAC = None
    
    def GenerateQMAC(self):
        # Do quantum stuff with the data here
        # Convert self.data to binary, apply quantum hashing and store in QMAC
        qmac = ""
        for char in self.data:
            qmac += str(qhash.start_qhash(char))
        return qmac
    
    def CombineDataQMAC(self):
        # Adding a delimiter :::: to distinguish data from QMAC and combining
        return (self.data + delim + self.QMAC)
    
    def SeparateDataQMAC(self,raw_data):
        # Split up the raw data
        parts = raw_data.split(delim)
        self.data = parts[0]
        self.QMAC = parts[1]
    
    def VerifyQMAC(self):
        # Return true if the QMAC with data matches the QMAC attached
        tmp = self.GenerateQMAC()
        print(f"Received QMAC: {self.QMAC}")
        print(f"QMAC from message: {tmp}")
        if tmp == self.QMAC:
            return True
        else:
            return False
    
    def Encrypt(self):
        # Assume that encryption is just reversing string
        self.data = self.data[::-1]

    def Decrypt(self):
        # Decryption would again just be reversing string
        self.data = self.data[::-1]
            
def sender(dest_port=12345):
    # Create a TCP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    dest_addr = '127.0.0.1' 
    #dest_port = 12346 to simulate MiTM, sender sends to the port the MiTM listens on, by default it is the acutal server's port

    # Craft the data to send
    raw_data = input("Enter the message to send: ")
    qpacket = QPacket(raw_data)
    qpacket.QMAC = qpacket.GenerateQMAC() # generate MAC
    print(f"Sender generated QMAC: {qpacket.QMAC}")
    qpacket.Encrypt() # encrypt data
    data = (qpacket.CombineDataQMAC()).encode() # combining and encode to send

    try:
        sock.connect((dest_addr, dest_port))
        sock.sendall(data)
        print("Packet sent successfully.")
    except Exception as e:
        print("Error sending packet:", e)
    finally:
        sock.close()

def reciever():

    def handle_client(client_socket):
        raw_data = client_socket.recv(1024)

        if raw_data:
            encry_data = raw_data.decode()
            qpacket = QPacket(None)
            qpacket.SeparateDataQMAC(encry_data)
            qpacket.Decrypt()
            if qpacket.VerifyQMAC():
                print("Accept! No tampering.")
            else:
                print("Discard! Data has been tampered.")
        else:
            print("Client disconnected")
        client_socket.close()
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    host = '127.0.0.1'
    port = 12345

    try:
        # Bind to socket
        sock.bind((host, port))
        
        # recv the data
        sock.listen(5)
        print(f"Server listening on {host}:{port}")
        while True:
            # Accept incoming connections
            client_socket, client_address = sock.accept()
            print(f"Connection from {client_address}")

            # Handle the client connection
            handle_client(client_socket)
    except Exception as e:
        print("Error rcving packet:", e)
    finally:
        # Close the socket
        sock.close()

def mitm():
    port = 12346
    host = '127.0.0.1'
    dest_addr = '127.0.0.1'
    dest_port = 12345
    tampered_data = bad_data

    def handle_client(client_socket):
        raw_data = client_socket.recv(1024)

        if raw_data:
            encry_data = raw_data.decode()
            qpacket = QPacket(None)
            qpacket.SeparateDataQMAC(encry_data)
            #qpacket.Decrypt() # MiTM doesn't know how to decrypt, they can only change the data and leave MAC as it is
        else:
            print("Client disconnected")
        client_socket.close()
        return qpacket.QMAC

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # Bind to socket
        sock.bind((host, port))

        # recv the data
        sock.listen(10)
        print(f"MiTM listening on {host}:{port}")
        while True:
            # make a connection to actual server
            sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock2.connect((dest_addr, dest_port))

            # Accept incoming connections
            client_socket, client_address = sock.accept()
            print(f"Connection from {client_address}")

            # Eavesdrop client connection
            original_QMAC = handle_client(client_socket)
            
            # Generate Tampered data and send
            qpacket = QPacket(tampered_data)
            qpacket.QMAC = original_QMAC # MiTM can't do anything, so assuming the original MAC is left as is. adversary cannot encrypt either because they haven't set up the key
            
            # send the tampered data and close the socket connecting to actual server
            data = (qpacket.CombineDataQMAC()).encode()
            sock2.sendall(data)
            sock2.close()
    except Exception as e:
        print("Error rcving packet:", e)
    finally:
        sock.close()

def main():
    if len(sys.argv) >= 1:
        mode = sys.argv[1] # 0-sender , 1-reciever , 2-MiTM
        if(mode=='0'):
            if sys.argv[2]=='0': # 0 means no MiTM
                sender()
            else:   # means MiTM
                sender(12346)
        elif(mode=='1'):
            reciever()
        elif(mode=='2'):
            mitm()
        else:
            print("wrong")

if __name__ == "__main__":
    main()