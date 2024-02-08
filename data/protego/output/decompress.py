import argparse
import gzip
import json
import pickle


def main(args):
    input_fn = args.input

    with gzip.open(input_fn, 'rb') as input_f:
        data = pickle.load(input_f)
        print(len(data.keys()))

    # with open(f'{input_fn}.pkl', 'wb') as output_f:
    #     pickle.dump(dao, output_f)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='Input file (JSON)', required=True)

    args_ = parser.parse_args()
    main(args_)
