from news.common.folder_file import FolderFile
from news.common.handle_time import TakeTime
from news.keywords.occurrences_of_word import occurrences_of_word


def oof(
    assets: str = './assets',
    source_path: str = './assets/json',
    date_duration: int = 0,
    star_date: str = TakeTime.now_datetime(),
    name: str = None,
    rest: bool = True,
):

    file_path_list = FolderFile(source_path=source_path,
                                end_date=star_date,
                                date_duration=date_duration).get_file_path_list()
    occurrences_of_word(file_path_list, name, assets, rest)


if __name__ == "__main__":
    name = 'contents_word_segmenter'
    name = 'contents_all_filters'
    oof(star_date='2022-06-27', date_duration=0, name=name, rest=True)
