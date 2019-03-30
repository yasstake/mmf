

PRICE_UNIT=0.5
BOOK_DEPTH = 128

LAYER_BUY_BOOK = 0
LAYER_SELL_BOOK = 1
LAYER_BUY_TRADE = 2
LAYER_SELL_TRADE = 3

FORCAST_TIME = 600

ORDER_BOOK_DATA_LIMIT = 100

LOG_PROJECT_NAME = 'bitmmf'
LOG_BUCKET_NAME= 'mmflog'

TIME_WIDTH = 128
BOARD_WIDTH = 32
BOARD_TIME_WIDTH = TIME_WIDTH
NUMBER_OF_LAYERS = 4


class ACTION:
    NOP =           0
    BUY =      0b0001
    SELL =     0b0010
    BUY_NOW =  0b0100
    SELL_NOW = 0b1000
