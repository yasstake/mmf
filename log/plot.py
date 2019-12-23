from log.dbgen import Generator


def show():
    g = Generator()
    gen1 = g.create(db_name='/bitlog/bitlog.db')

    i = 0
    for board in gen1:
        i += 1
        board.save_to_img('./', i)

        if 1 < i:
            break


if __name__ == "__main__":
    show()

