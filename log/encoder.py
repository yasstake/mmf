

def encode(message):
    message = message.replace(',"price":', ',p:')
    message = message.replace(',"size":', ',s:')
    message = message.replace('"id":', 'i:')
    message = message.replace('"side"', '"S"')
    message = message.replace('"types"', '"T"')
    message = message.replace('"table"', '"t"')
    message = message.replace('"Sell"', '"H"')
    message = message.replace('"Buy"', '"L"')
    message = message.replace('"orderBookL2"', '"O"')
    message = message.replace('"action"', '"A"')
    message = message.replace('"update"', '"U"')
    message = message.replace('"data"', '"d"')
    return message


def decode(message):
    message = message.replace(',p:', ',"price":')
    message = message.replace(',s:', ',"size":')
    message = message.replace('i:', '"id":')
    message = message.replace('"S"', '"side"')
    message = message.replace('"T"', '"types"')
    message = message.replace('"t"', '"table"')
    message = message.replace('"H"', '"Sell"')
    message = message.replace('"L"', '"Buy"')
    message = message.replace('"O"', '"orderBookL2"')
    message = message.replace('"A"', '"action"')
    message = message.replace('"U"', '"update"')
    message = message.replace('"d"', '"data"')
    return message

