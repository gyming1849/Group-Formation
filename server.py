import copy
import logging
import random
import socket
import pickle
import threading
from itertools import combinations

import numpy as np
from multiprocessing import shared_memory
import time
import os
import struct
import stop
from config import Config
from constants import Constants
from message import Message, MessageTypes
import worker
import utils
import sys
import matplotlib.pyplot as plt
import matplotlib as mpl
from collections import Counter
from utils import dict_hash

# mpl.use('macosx')

test = True
hd_timer = None
hd_round = []
hd_time = []
should_stop = False


def set_stop():
    global should_stop
    should_stop = True
    print('will stop next round')


def query_cliques_client(connection):
    query_msg = Message(MessageTypes.QUERY_CLIQUES)
    connection.send(pickle.dumps(query_msg))


def pull_cliques_client(connection):
    data = recv_msg(connection)
    message = pickle.loads(data)
    # print(message.args[0], message.args[1])
    return message.args[0], message.args[1], message.args[2]  # cliques, connections, neighbors


def stop_client(connection):
    stop_msg = Message(MessageTypes.STOP)
    connection.send(pickle.dumps(stop_msg))
    # data = connection.recv(2048)
    # message = pickle.loads(data)
    # return message.args[0]


def aggregate_cliques(indexes, sh_arrs):
    all_cliques = dict()
    all_connections = dict()
    all_neighbors = dict()
    sh_arrays = copy.deepcopy(sh_arrs)
    for k in indexes:
        all_connections[k + 1] = sh_arrays[k][:G]
        all_neighbors[k + 1] = sh_arrays[k][G]
        clique_key = ".".join([str(clique) for clique in sh_arrays[k][:G]])
        if clique_key in all_cliques:
            all_cliques[clique_key] += 1
        else:
            all_cliques[clique_key] = 1

    return all_cliques, all_connections, Counter(list(all_neighbors.values()))


def get_shape_floor_center(arr):
    length = arr.shape[0]
    sum_x = np.sum(arr[:, 0])
    sum_y = np.sum(arr[:, 1])
    return np.array([sum_x / length, sum_y / length, 0])


def get_shape_floor_radius(arr, center):
    arr_projected_floor = np.copy(arr)
    arr_projected_floor[:, 2] = 0
    return np.max(np.linalg.norm(arr_projected_floor - center, axis=1))


def get_dispatchers_for_shape(shape, num_dispatchers=Config.NUM_DISPATCHERS):
    if num_dispatchers == 1:
        return [np.array([0.0, 0.0, 0.0])]

    center = get_shape_floor_center(shape)
    r = get_shape_floor_radius(shape, center)
    dispatcher_coordinates = []
    for k in range(num_dispatchers):
        phi = 2 * np.pi * k / num_dispatchers
        dispatcher_coordinates.append(center + np.array([r * np.cos(phi), r * np.sin(phi), 0]))
    return dispatcher_coordinates


def assign_dispatcher(fid, dispatchers):
    return dispatchers[fid % len(dispatchers)]


def send_msg(sock, msg):
    # Prefix each message with a 4-byte big-endian unsigned integer (network byte order)
    msg = struct.pack('>I', len(msg)) + msg
    sock.sendall(msg)


def recv_msg(sock):
    # Read message length and unpack it into an integer
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    # Read the message data
    return recvall(sock, msglen)


def recvall(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data


def wait_for_client(sock):
    sock.recv(1)
    sock.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename='your_log_file.log')
    print('multicast' if Config.MULTICAST else 'broadcast')
    N = 1
    nid = 0
    experiment_name = str(int(time.time()))
    server_address = Constants.SERVER_ADDRESS
    if len(sys.argv) > 1:
        N = int(sys.argv[1])
        nid = int(sys.argv[2])
        experiment_name = sys.argv[3]
        server_address = (Constants.SERVER_ADDRESS[0], int(sys.argv[4]))

    IS_CLUSTER_SERVER = N != 1 and nid == 0
    IS_CLUSTER_CLIENT = N != 1 and nid != 0

    if IS_CLUSTER_SERVER:
        ServerSocket = socket.socket()
        ServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        while True:
            try:
                ServerSocket.bind(server_address)
            except OSError:
                time.sleep(10)
                continue
            break
        ServerSocket.listen(N-1)

        clients = []
        for i in range(N-1):
            client, address = ServerSocket.accept()
            print(address)
            clients.append(client)

    if IS_CLUSTER_CLIENT:
        client_socket = socket.socket()
        while True:
            try:
                client_socket.connect(server_address)
            except OSError:
                time.sleep(10)
                continue
            break

    G = Config.G
    FILE_NAME_KEYS = Config.FILE_NAME_KEYS

    dir_name = None
    if not Config.DEBUG:
        from datetime import datetime

        current_date_time = datetime.now().strftime("%H:%M:%S_%m:%d:%Y")
        if len(FILE_NAME_KEYS):
            keys = "_".join(f"{k}{Config.__getattribute__(Config, k)}" for k in FILE_NAME_KEYS)
        else:
            keys = current_date_time
        file_name = f"{Config.SHAPE}_{keys}_{experiment_name}"

        if len(Config.DIR_KEYS):
            dir_name = "_".join(f"{k}{Config.__getattribute__(Config, k)}" for k in Config.DIR_KEYS)

    main_dir = Config.RESULTS_PATH if dir_name is None else os.path.join(Config.RESULTS_PATH, Config.SHAPE, dir_name)
    results_directory = os.path.join(main_dir, experiment_name)
    shape_directory = main_dir
    figure_directory = os.path.join(shape_directory, 'figures')
    # print(results_directory)
    # exit()
    if not Config.DEBUG:
        if not os.path.exists(results_directory):
            os.makedirs(os.path.join(results_directory, 'json'), exist_ok=True)
        if not os.path.exists(figure_directory):
            os.makedirs(figure_directory, exist_ok=True)

    if Config.TEST_ENABLED:
        r2 = 1
        r1 = r2 * Config.R
        n1 = Config.NUMBER_OF_FLSS // G
        n2 = G

        points = []
        for i in range(n1):
            theta = i * 2 * np.pi / n1
            c1 = [r1 * np.cos(theta), r1 * np.sin(theta), 0]
            for j in range(n2):
                alpha = theta + j * 2 * np.pi / n2
                point = [c1[0] + r2 * np.cos(alpha), c1[1] + r2 * np.sin(alpha), 0]
                points.append(point)

        point_cloud = np.array(points)

    else:
        if Config.READ_FROM_NPY:
            with open(f'results/{Config.READ_FROM_NPY}.npy', 'rb') as f:
                point_cloud = np.load(f)
        else:
            point_cloud = np.loadtxt(f'assets/{Config.SHAPE}.txt', delimiter=',')

        if Config.SAMPLE_SIZE != 0:
            np.random.shuffle(point_cloud)
            point_cloud = point_cloud[:Config.SAMPLE_SIZE]

    total_count = point_cloud.shape[0]

    gtl_point_cloud = np.random.uniform(0, 5, size=(total_count, 3))
    sample = np.zeros(G + 1, dtype=np.int32)

    node_point_idx = []
    for i in range(total_count):
        if i % N == nid:
            node_point_idx.append(i)
        gtl_point_cloud[i] = np.array([point_cloud[i][0], point_cloud[i][1], point_cloud[i][2]])
        print(i, gtl_point_cloud[i])
    for i in range(total_count, total_count+12):
        node_point_idx.append(i)
    count = len(node_point_idx)
    print(count)

    dispatchers = get_dispatchers_for_shape(gtl_point_cloud)
    processes = []
    shared_arrays = dict()
    shared_memories = dict()

    shared_arrays_fls = dict()
    shared_memories_fls = dict()

    local_gtl_point_cloud = []

    try:

        for i in node_point_idx:
            shm = shared_memory.SharedMemory(create=True, size=sample.nbytes)
            shared_array = np.ndarray(sample.shape, dtype=sample.dtype, buffer=shm.buf)
            shared_array[:G] = i + 1
            shared_array[G] = 0

            shared_arrays[i] = shared_array
            shared_memories[i] = shm
            if i < point_cloud.shape[0]:
                local_gtl_point_cloud.append(gtl_point_cloud[i])
                dispatcher = gtl_point_cloud[i]


            # if Config.H == 2:
            #     sorted_neighbors = knn_idx[i][1:] + 1
            #     sorted_neighbors = sorted_neighbors.tolist()
            #     dists = knn_dists[i][1:]
            # else:
            sorted_neighbors = []
            dists = []
            # fid_to_dist = dict(zip(sorted_neighbors, knn_dists[i][1:]))

            # dispatcher = assign_dispatcher(i+1, dispatchers)

            if i >= point_cloud.shape[0]:
                p = worker.WorkerProcess(
                    count, i + 1, gtl_point_cloud[i - point_cloud.shape[0]],
                    gtl_point_cloud[i - point_cloud.shape[0]], shm.name, results_directory,
                    # count, i + 1, gtl_point_cloud[random.randint(0, point_cloud.shape[0]-1)], gtl_point_cloud[random.randint(0, point_cloud.shape[0]-1)], shm.name, results_directory,
                    G, sorted_neighbors, dists, is_cluster=True)
            else:
                p = worker.WorkerProcess(
                count, i + 1, gtl_point_cloud[i], dispatcher, shm.name, results_directory,
                G, sorted_neighbors, dists, is_cluster=False)
            p.start()
            processes.append(p)
    except OSError as e:
        print(e)
        for p in processes:
            p.terminate()
        for s in shared_memories:
            s.close()
            s.unlink()
        exit()

    # gtl_point_cloud = local_gtl_point_cloud

    start_time = time.time()
    is_failed = False
    # print('waiting for processes ...')

    freeze_timer = start_time
    last_hash = None

    if IS_CLUSTER_CLIENT:
        while True:
            server_msg = client_socket.recv(2048)
            server_msg = pickle.loads(server_msg)

            if server_msg.type == MessageTypes.QUERY_CLIQUES:
                client_cliques, client_connections, client_neighbors = aggregate_cliques(node_point_idx, shared_arrays)
                response = Message(MessageTypes.REPLY_CLIQUES, args=(client_cliques, client_connections, client_neighbors))
                # client_socket.sendall(pickle.dumps(response))
                send_msg(client_socket, pickle.dumps(response))
            elif server_msg.type == MessageTypes.STOP:
                break
    else:
        while True:
            cur_time = time.time()
            cliques, connections, neighbors = aggregate_cliques(node_point_idx, shared_arrays)

            if IS_CLUSTER_SERVER:
                for i in range(N-1):
                    query_cliques_client(clients[i])

            if IS_CLUSTER_SERVER:
                for i in range(N-1):
                    client_clique, client_connection, client_neighbors = pull_cliques_client(clients[i])
                    neighbors += client_neighbors
                    for key, con in client_connection.items():
                        connections[key] = con
                    for key, size in client_clique.items():
                        if key in cliques:
                            cliques[key] += size
                        else:
                            cliques[key] = size



            clique_sizes = filter(lambda x: x == G, cliques.values())
            single_sizes = filter(lambda x: x == 1, cliques.values())
            d_hash = dict_hash(cliques)
            if d_hash != last_hash:
                freeze_timer = cur_time

            if cur_time - freeze_timer >= Config.SERVER_TIMEOUT:
                is_failed = True
                print(cliques)
                break
            last_hash = d_hash
            # print(cliques)
            if len(list(clique_sizes)) == total_count // G and len(list(single_sizes)) == total_count % G:
                print(cliques)
                # print(connections)
                break

            time.sleep(.04)

    if nid == 0:
        end_time = cur_time

    if nid == 0:
        stop.stop_all()
    print("done")

    if IS_CLUSTER_SERVER:
        for i in range(N - 1):
            stop_client(clients[i])

        client_threads = []
        for client in clients:
            t = threading.Thread(target=wait_for_client, args=(client,))
            t.start()
            client_threads.append(t)
        for t in client_threads:
            t.join()

        ServerSocket.close()

    for p in processes:
        p.join(Config.PROCESS_JOIN_TIMEOUT)
        if p.is_alive():
            break

    for p in processes:
        if p.is_alive():
            p.terminate()

    if nid == 0:
        visited = set()
        fig = plt.figure()
        # ax = fig.add_subplot(projection='3d')
        ax = fig.add_subplot()
        ax.set_aspect('equal')
        avg_distances = []
        min_distances = []
        max_distances = []
        num_cliques = 0
        num_singles = 0
        for c in connections.values():
            key = str(c)
            if key in visited:
                continue
            visited.add(key)

            group_points = [gtl_point_cloud[ci - 1] for ci in c]
            num_members = len(set(c))
            if num_members == G:
                c_count = 0
                dists = []
                for el_i, el_j in combinations(group_points, 2):
                    dists.append(np.linalg.norm(el_i - el_j))
                    c_count += 1
                avg_distances.append(sum(dists) / c_count)
                min_distances.append(min(dists))
                max_distances.append(max(dists))
                num_cliques += 1
            elif num_members == 1:
                num_singles += 1
            xs = [p[0] for p in group_points]
            ys = [p[1] for p in group_points]
            zs = [p[2] for p in group_points]
            # ax.plot3D(xs + [xs[0]], ys + [ys[0]], zs + [zs[0]], '-o')
            ax.plot(xs + [xs[0]], ys + [ys[0]], '-o')
        # plt.savefig(f'{Config.RESULTS_PATH}/{experiment_name}.jpg')
        if Config.DEBUG:
            plt.show()
        else:
            plt.savefig(os.path.join(figure_directory, f'{file_name}.jpg'), dpi=300)

    if not Config.DEBUG and nid == 0:  # and not is_failed:
        # if N == 1:
        num_cliques_d = 1 if num_cliques == 0 else num_cliques
        utils.create_csv_from_json(results_directory, end_time-start_time)
        min_distances = [-1] if len(min_distances) == 0 else min_distances
        avg_distances = [-1] if len(avg_distances) == 0 else avg_distances
        max_distances = [-1] if len(max_distances) == 0 else max_distances
        rows = [["metric", "value"],
                ["duration", end_time-start_time],
                ["min min_dists", min(min_distances)],
                ["avg min_dists", sum(min_distances) / num_cliques_d],
                ["max min_dists", max(min_distances)],
                ["min avg_dists", min(avg_distances)],
                ["avg avg_dists", sum(avg_distances) / num_cliques_d],
                ["max avg_dists", max(avg_distances)],
                ["min max_dists", min(max_distances)],
                ["avg max_dists", sum(max_distances) / num_cliques_d],
                ["max max_dists", max(max_distances)],
                ["number of cliques", num_cliques],
                ["number of single nodes", num_singles],
                ["frequency of clique consensus", str(Counter(list(cliques.values())))],
                ["frequency of neighbors", str(neighbors)]
                ]
        utils.write_csv(results_directory, rows, 'metrics')
        utils.write_configs(results_directory, current_date_time)
        utils.combine_csvs(results_directory, shape_directory, file_name)

    for s in shared_memories.values():
        s.close()
        s.unlink()

    if IS_CLUSTER_CLIENT:
        time.sleep(10)
        client_socket.send(struct.pack('b', True))
        client_socket.close()
