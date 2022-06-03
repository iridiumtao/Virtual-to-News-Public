# -*- coding:utf-8 -*-
import pandas as pd
from article import Article as Ar


def main():
    source_path = "assets/json/test186.json"
    output_path = "assets/json/keyword/test186_keyword.json"

    # read json database
    database = pd.read_json(source_path)
    database = database.transpose()

    # get content and title of database
    title = database["title"]
    content = database["content"]

    # Title and content combinations
    content_list = []
    for x, y in zip(title, content):
        content_list.append(x + '\n' + y)

    # ar_content=content.apply(ar) # to do:df usage

    # get keyword
    ar_content = Ar(content_list)
    category = ar_content.get_keyword()

    # category save to json
    database["category"] = category
    database.to_json(output_path, orient='index', force_ascii=False, indent=4)


if __name__ == "__main__":
    main()
