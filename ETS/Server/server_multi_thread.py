import socket
import logging
import json
import threading
import os
import ssl

alldata = dict()
alldata['1'] = dict(nomor=1, nama="pete", posisi="kiper")
alldata['2'] = dict(nomor=2, nama="shawn", posisi="bek kiri")
alldata['3'] = dict(nomor=3, nama="kim", posisi="bek kanan")
alldata['4'] = dict(nomor=4, nama="leon", posisi="bek tengah kanan")
alldata['5'] = dict(nomor=5, nama="arnold", posisi="striker")
alldata['6'] = dict(nomor=6, nama="jake", posisi="midfielder")
alldata['7'] = dict(nomor=7, nama="kevin", posisi="foward")
alldata['8'] = dict(nomor=8, nama="will", posisi="striker")
alldata['9'] = dict(nomor=9, nama="rock", posisi="foward")
alldata['10'] = dict(nomor=10, nama="chris", posisi="kiper")


def proses_request(request_string):
    cstring = request_string.split(" ")
    hasil = None
    try:
        command = cstring[0].strip()
        if (command == 'getdatapemain'):
            nomor_pemain = cstring[1].strip()
            try:
                logging.warning(f"data {nomor_pemain} ketemu")
                hasil = alldata[nomor_pemain]
            except:
                hasil = None
    except:
        hasil = None
    return hasil


def serialize(a):
    serialized = json.dumps(a)
    logging.warning(f"serialized data : {serialized}")
    return serialized


def run_server(server_address, is_secure=False):
    if is_secure:
        print(os.getcwd())
        cert_location = os.getcwd() + '/certs/'
        socket_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        socket_context.load_cert_chain(
            certfile=cert_location + 'domain.crt',
            keyfile=cert_location + 'domain.key'
        )

    # --- INISIALISATION ---
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Bind the socket to the port
    logging.warning(f"starting up on {server_address}")
    sock.bind(server_address)
    # Listen for incoming connections
    sock.listen(1000)

    # Threads
    threads = dict()
    thread_count = 0

    while True:
        # Wait for a connection
        logging.warning("waiting for a connection")
        connection, client_address = sock.accept()

        if is_secure:
            connection = socket_context.wrap_socket(connection, server_side=True)
        else:
            connection = connection

        logging.warning(f"Incoming connection from {client_address}")

        # Receive the data in small chunks and retransmit it
        try:
            logging.warning("started a new thread")
            threads[thread_count] = threading.Thread(target=process_connection, args=(client_address, connection))
            threads[thread_count].start()
            thread_count += 1
        except ssl.SSLError as error_ssl:
            logging.warning(f"SSL error: {str(error_ssl)}")


def process_connection(client_address, connection):
    selesai = False
    data_received = ""  # string
    while True:
        data = connection.recv(32)
        logging.warning(f"received {data}")
        if data:
            data_received += data.decode()
            if "\r\n\r\n" in data_received:
                selesai = True

            if selesai:
                hasil = proses_request(data_received)
                logging.warning(f"hasil proses: {hasil}")

                hasil = serialize(hasil)
                hasil += "\r\n\r\n"
                connection.sendall(hasil.encode())
                break

        else:
            logging.warning(f"no more data from {client_address}")
            break
    # Clean up the connection
    logging.warning("thread ended")


if __name__ == '__main__':
    try:
        run_server(('0.0.0.0', 16000), True)
    except KeyboardInterrupt:
        logging.warning("Control-C: Program berhenti")
        exit(0)
    finally:
        logging.warning("selesai")
