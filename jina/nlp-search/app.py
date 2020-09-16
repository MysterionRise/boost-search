import argparse
import os
from tempfile import mkdtemp

from jina.flow import Flow

os.environ['PARALLEL'] = str(1)
os.environ['SHARDS'] = str(1)


def index(arg_ns: argparse.Namespace):
    print('indexing data...')
    f = Flow().load_config('flow-index.yml')
    with f:
        f.index_lines(filepath=arg_ns.data, size=arg_ns.num_docs, batch_size=16)


def query(arg_ns: argparse.Namespace):
    print('querying...')
    flow = Flow().load_config('flow-query.yml')
    with flow.build() as fl:
        if arg_ns.text:
            ppr = lambda x: print_topk(x, arg_ns.text)
            fl.search_lines(lines=[arg_ns.text, ], output_fn=ppr, top_k=arg_ns.top_k)


def print_topk(resp, word):
    for d in resp.search.docs:
        print(f'Ta-Dah🔮, here are what we found for: {word}')
        for idx, match in enumerate(d.matches):
            score = match.score.value
            if score <= 0.0:
                continue
            if len(match.chunks) > 0:
                word_def = match.chunks[0].text
            else:
                word_def = ""
            word = match.meta_info.decode()
            print('> {:>2d}({:.2f}). {}: "{}"'.format(idx, score, word, word_def.strip()))


if __name__ == '__main__':
    tmp = mkdtemp()[1]
    print(tmp)
    os.environ['TMP_WORKSPACE'] = tmp

    parser = argparse.ArgumentParser(description='Urban dictionary search')

    subparsers = parser.add_subparsers(help='select mode: index, query')

    parser_index = subparsers.add_parser('index')
    parser_index.set_defaults(func=index)
    parser_index.add_argument(
        '--data',
        type=str,
        default='urbandict-word-defs.csv',
        help='Location of urbandict csv file'
    )

    parser_index.add_argument(
        '--num-docs',
        type=int,
        default=50,
        help='Number of documents to be indexed'
    )

    parser_query = subparsers.add_parser('query')
    parser_query.set_defaults(func=query)
    parser_query.add_argument(
        '--top-k',
        type=int,
        default=10,
        help='Top K documents to be returned'
    )
    parser_query.add_argument(
        '--text',
        type=str,
        help='Specify the query text'
    )

    args = parser.parse_args()
    args.func(args)
