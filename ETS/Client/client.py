import datetime
import random
import sys
import socket
import json
import logging
import threading

import xmltodict
import ssl
import os

default_server_address = ('172.16.16.101', 16000)


def make_socket(destination_address='localhost', port=12000):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (destination_address, port)
        # logging.warning(f"connecting to {server_address}")
        sock.connect(server_address)
        return sock
    except Exception as ee:
        logging.warning(f"error {str(ee)}")


def make_secure_socket(destination_address='localhost', port=10000):
    try:
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.verify_mode = ssl.CERT_OPTIONAL
        context.load_verify_locations(os.getcwd() + '/domain.crt')

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (destination_address, port)
        # logging.warning(f"connecting to {server_address}")
        sock.connect(server_address)
        secure_socket = context.wrap_socket(sock, server_hostname=destination_address)
        # logging.warning(secure_socket.getpeercert())
        return secure_socket
    except Exception as ee:
        logging.warning(f"error {str(ee)}")


def deserialisasi(s):
    # logging.warning(f"deserialisasi {s.strip()}")
    return json.loads(s)


def send_command(command_str, is_secure=False):
    alamat_server = default_server_address[0]
    port_server = default_server_address[1]
    if is_secure:
        sock = make_secure_socket(alamat_server, port_server)
    else:
        sock = make_socket(alamat_server, port_server)

    # logging.warning(f"connecting to {default_server_address}")
    try:
        # logging.warning(f"sending message ")
        sock.sendall(command_str.encode())

        data_received = ""  # empty string
        # logging.warning("waiting server response")

        while True:
            data = sock.recv(16)
            if data:
                data_received += data.decode()
                if "\r\n\r\n" in data_received:
                    break
            else:
                break
        hasil = deserialisasi(data_received)
        # logging.warning(f"data received from server: {hasil}")
        return hasil
    except Exception as ee:
        # logging.warning(f"error during data receiving {str(ee)}")
        return False


def get_data_pemain(nomor=0, is_secure=False):
    cmd = f"getdatapemain {nomor}\r\n\r\n"
    hasil = send_command(cmd, is_secure)
    if hasil:
        print(f"nama : {hasil['nama']}, nomor pemain : {hasil['nomor']}")
    else:
        print(f"gagal mendapatkan pemain bernomor {nomor}")


def get_data_beberapa_pemain(amount, is_secure=False):
    for request in range(amount):
        get_data_pemain(random.randint(1, 10), is_secure)


def start_thread(thread_count=1, request_amount_per_thread=1, is_secure=False):
    threads = dict()

    waktu_awal = datetime.datetime.now()
    for thread in range(thread_count):
        threads[thread] = threading.Thread(target=get_data_beberapa_pemain,
                                           args=(request_amount_per_thread, is_secure))
        threads[thread].start()

    for thread in range(thread_count):
        threads[thread].join()

    waktu_akhir = datetime.datetime.now()
    print(
        f"total waktu untuk menjalankan {thread_count} thread adalah {waktu_akhir - waktu_awal}")


if __name__ == '__main__':
    start_thread(20, 5, True)
