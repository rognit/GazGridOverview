SQUARE_SIZE = 200

# preset parameters
BUFFER_DISTANCE = 200  # meters
ORANGE_THRESHOLD = 250  # people
RED_THRESHOLD = 2500  # people
MERGING_THRESHOLD = 50  # meters
MAX_MERGING_THRESHOLD = 1000  # meters
IGNORING_THRESHOLD = 600  # meters

# initial raw data (before setup)
INIT_POPULATION_PATH = 'resources/raw/carreaux_200m_met.csv'
INIT_GRT_PATH = 'resources/raw/trace-du-reseau-grt-250.csv'
INIT_TEREGA_PATH = 'resources/raw/terega-trace-du-reseau.csv'

# base data (after setup)
BASE_POPULATION_PATH = 'resources/base_population.csv'
BASE_GAZ_NETWORK_PATH = 'resources/base_gaz_network.csv'

# computed data (with preset parameters)
SIMPLIFIED_COMPUTED_GAZ_NETWORK_PATH = 'resources/simplified_computed_gaz_network.csv'
EXHAUSTIVE_COMPUTED_GAZ_NETWORK_PATH = 'resources/exhaustive_computed_gaz_network.csv'
