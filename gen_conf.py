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
    "G": "3",
    "SHAPE": "test",
    "RESULTS_PATH": "results",
    "DEBUG": "False",
    "FILE_NAME_KEYS": "['G']",
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
    "H": "canf",  # valid values for heuristic: simpler, canf, vns, rs
    "VNS_TIMEOUT": "0.1",
    "EXPANSION_TIMEOUT": "0.05",
    "ETA": "G - 1",  # initial eta only effective for H = simpler and H = rs
    "ETA_STR": "G-1",
}

general_props = [
    {
        "keys": ["SHAPE"],
        "values": ["'chess'", "'dragon'"]
    },
    {
        "keys": ["G"],
        "values": ["3", "15"]
    },
    {
        "keys": ["H"],
        "values": ["'simpler'", "'canf'", "'vns'", "'rs'"]
    },

    # you can combine multiple properties if you don't need all the combinations
    # {
    #     "keys": ["SHAPE", "G"],
    #     "values": [
    #         {"SHAPE": "'chess'", "G": "3"},
    #         {"SHAPE": "'dragon'", "G": "20"},
    #     ]
    # },
]

if __name__ == '__main__':
    file_name = "config"
    class_name = "Config"
    directory_path = "experiments"
    props = general_props
    def_conf = def_general_conf

    props_values = [p["values"] for p in props]
    print(props_values)
    combinations = list(itertools.product(*props_values))
    print(f"Generated {len(combinations)} config files in {directory_path}")

    try:
        if os.path.exists('experiments'):
            os.rmdir(directory_path)
        os.makedirs(directory_path, exist_ok=True)
    except OSError as e:
        print(f"Error: {e}")

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
