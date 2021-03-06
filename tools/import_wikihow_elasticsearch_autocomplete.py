import json, sys, io, os
from argparse import ArgumentParser
from elasticsearch import Elasticsearch
from argparse import ArgumentParser


def main():
    parser = ArgumentParser()
    parser.add_argument("-d", "--data", dest="data", help="path to dataset", metavar="DATA")
    parser.add_argument("-i", "--index", dest="index", help="elasticsearch index", metavar="INDEX")
    parser.add_argument("-t", "--timeout", dest="timeout",
                        help="maximum wait time in seconds for success of one bulk import", metavar="TIMEOUT")
    args = parser.parse_args()

    if not args.data or not args.index:
        parser.print_help()
        return

    timeout = 30
    if args.timeout:
        timeout = int(float(args.timeout))

    # init es
    es = Elasticsearch(['localhost'], port=9200)

    # define mapping
    index = args.index
    mapping = {
        "mappings": {
            "_doc": {
                "properties": {
                    "article": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                                "type": "keyword",
                                "ignore_above": 256
                            }
                        }
                    },
                    "filename": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                                "type": "keyword",
                                "ignore_above": 256
                            }
                        }
                    },
                    "full_article": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                                "type": "keyword",
                                "ignore_above": 256
                            }
                        }
                    },
                    "summary": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                                "type": "keyword",
                                "ignore_above": 256
                            }
                        }
                    },
                    "title": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                                "type": "keyword",
                                "ignore_above": 256
                            }
                        }
                    },
                    "suggest_title": {
                        "type": "completion",
                        "max_input_length": 100
                    },
                }
            }
        }
    }

    # create index (delete old if necessary!)
    if es.indices.exists(index):
        print("deleting '%s' index..." % index)
        res = es.indices.delete(index=index)
        print(" response: '%s'" % res)
    print("creating '%s' index..." % index)
    res = es.indices.create(index=index, body=mapping)
    print(" response: '%s'" % res)

    # import data
    id = 0
    dataset_path = os.path.normpath(args.data)
    for entry in os.scandir(dataset_path):
        filepath = entry.path
        filename = entry.name
        if filename.endswith(".json"):
            print("Indexing " + filename)
            with io.open(filepath, 'r', encoding="utf8") as file:
                json_data = json.load(file)
                json_data['filename'] = filename
                json_data['suggest_title'] = json_data['title']
                es.index(index=args.index, doc_type="_doc", id=id, body=json_data)
                id = id + 1
        else:
            continue


if __name__ == "__main__":
    main()
