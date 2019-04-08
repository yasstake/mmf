import sys
from log.price import PriceBoardDB
from log.logdb import LogDb

'''
usage

python3.7 db2img.py [dbname] [outdir]
'''

if __name__ == '__main__':

    if not len(sys.argv) == 3:
        print('python3.7 db2img.py [dbname] [outdir]')
        exit(-1)


    db_file = sys.argv[1]
    img_dir = sys.argv[2]

    print(db_file, img_dir)

    PriceBoardDB.export_db_to_img(db_file, img_dir)