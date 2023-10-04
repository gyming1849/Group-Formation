import itertools
import os

def_general_conf = {
    "INITIAL_RANGE": "1",
    "MAX_RANGE": "2000",
    "DROP_PROB_SENDER": "0",
    "DROP_PROB_RECEIVER": "0",
    "DEAD_RECKONING_ANGLE": "0",
    "ACCELERATION": "6",
    "DECELERATION": "6",
    "MAX_SPEED": "6",
    "DISPLAY_CELL_SIZE": "0.05",
    "BUSY_WAITING": "False",
    "SAMPLE_SIZE": "0",
    "DURATION": "600",
    "READ_FROM_NPY": "0",
    "K": "10",
    "SHAPE": "test90",
    "RESULTS_PATH": "results",
    "DEBUG": "False",
    "FILE_NAME_KEYS": "['K']",
    "DIR_KEYS": "['H']",
    "SERVER_TIMEOUT": "120",
    "PROCESS_JOIN_TIMEOUT": "120",
    "NUM_DISPATCHERS": "1",
    "MULTICAST": "True",
    "TIMELINE_LOG": "False",
    "OPT_SORT": "True",
    "TEST_ENABLED": "False",
    "NUMBER_OF_FLSS": "12",
    "R": "1",  # ratio of r2 to r1
    "H": "2.2",  # heuristic 1, 2.1, 2.2, vns, rs
    "VNS_TIMEOUT": "0.1",
    "EXPANSION_TIMEOUT": "0.05",
    "ETA": "K - 1",  # initial eta only effective for h:1 and h:rs
    "ETA_STR": "k-1",
}

general_props = [
    # {
    #     "keys": ["SHAPE", "K"],
    #     "values": [
    #         # {"SHAPE": "'chess'", "K": "3"},
    #         # {"SHAPE": "'chess'", "K": "20"},
    #         {"SHAPE": "'skateboard'", "K": "20"},
    #     ]
    # },
    # {
    #     "keys": ["H"],
    #     "values": ["2.2", "'rs'"]
    # },
]

if __name__ == '__main__':
    file_name = "config"
    class_name = "Config"
    props = general_props
    def_conf = def_general_conf

    props_values = [p["values"] for p in props]
    print(props_values)
    combinations = list(itertools.product(*props_values))
    print(len(combinations))

    if not os.path.exists('experiments'):
        os.makedirs('experiments', exist_ok=True)

    for j in range(len(combinations)):
        c = combinations[j]
        conf = def_conf.copy()
        for i in range(len(c)):
            for k in props[i]["keys"]:
                if isinstance(c[i], dict):
                    conf[k] = c[i][k]
                else:
                    conf[k] = c[i]
        with open(f'experiments/{file_name}{j}.py', 'w') as f:
            f.write(f'class {class_name}:\n')
            for key, val in conf.items():
                f.write(f'    {key} = {val}\n')
