import argparse
import gzip
import json
import pickle


def main(args):
    input_fn = args.input

    with open(input_fn, 'rb') as input_f:
        data = json.load(input_f)

    with gzip.open(f'{input_fn}.pkl.gzip', 'wb') as output_f:
        pickle.dump(data, output_f)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='Input file (JSON)', required=True)

    args_ = parser.parse_args()
    main(args_)
