

PRICE_UNIT=0.5
BOOK_DEPTH = 128

LAYER_BUY_BOOK = 0
LAYER_SELL_BOOK = 1
LAYER_BUY_TRADE = 2
LAYER_SELL_TRADE = 3

FORCAST_TIME = 360
PRICE_MARGIN = 0.0

ORDER_BOOK_DATA_LIMIT = 100

LOG_PROJECT_NAME = 'bitmmf'
LOG_BUCKET_NAME= 'mmflog'
BOARD_BUCKET_NAME = 'bitboard'
FULL_BOARD_BUCKET_NAME = 'fullbitboard'
ML_PACKAGE_BUCKET_NAME = 'mlpackage'

TIME_WIDTH = 60
BOARD_WIDTH = 30
BOARD_TIME_WIDTH = TIME_WIDTH
NUMBER_OF_LAYERS = 4

BOARD_IN_FILE = 600

class ACTION:
    NOP =      0
    BUY =      1
    BUY_NOW =  2
    SELL =     3
    SELL_NOW = 4

DEFAULT_TF_DATA_DIR = '/bitlog'
