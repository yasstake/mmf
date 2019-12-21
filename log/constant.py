

PRICE_UNIT = 0.5

TIME_WIDTH = 90
BOARD_WIDTH = 60


# width of order book width(both side)
BOOK_DEPTH = int(BOARD_WIDTH * 1.5)

LAYER_BUY_BOOK = 0
LAYER_SELL_BOOK = 1
LAYER_BUY_TRADE = 2
LAYER_SELL_TRADE = 3

FORECAST_TIME = 360
PRICE_MARGIN = 0.0

ORDER_BOOK_DATA_LIMIT = 100

LOG_PROJECT_NAME = 'bitmmf'
LOG_BUCKET_NAME= 'mmflog'
BOARD_BUCKET_NAME = 'bitboard'
FULL_BOARD_BUCKET_NAME = 'fullbitboard'
ML_PACKAGE_BUCKET_NAME = 'mlpackage'

BOARD_TIME_WIDTH = TIME_WIDTH + 1
NUMBER_OF_LAYERS = 4

BOARD_IN_FILE = 600


class ACTION:
    NOP = 0
    BUY = 1
    BUY_NOW = 2
    SELL = 3
    SELL_NOW = 4


DEFAULT_TF_DATA_DIR = '/bitlog'
MAX_SKIP_TIME = 100

TRAN_TIMEOUT = 600
MAKER_BUY = 1 - 0.00025
TAKER_BUY = 1.00075

MAKER_SELL = 1 + 0.00025
TAKER_SELL = 1 - 0.00075
