import os
import sys

from git import Repo
from loguru import logger

COMMITS_TO_PRINT = 5

BRANCH_NAME = 'server'


class GitCommand:
    @logger.catch
    def __init__(self, branch_name: str = BRANCH_NAME):
        # repo_path = os.getenv('NEWS_PATH')
        repo_path = os.path.abspath('')
        self.repo = Repo(path=repo_path)
        self.branch_name = branch_name
        if not self.repo.bare:
            logger.info('Repo at {} successfully loaded.'.format(repo_path))
            # self.desc_repository()
            # self.desc_commit()
            if branch_name not in self.repo.references or "origin/" + branch_name not in self.repo.references:
                logger.error(branch_name + " branch not in Repo")
                self.add_and_commit_and_push()
                self.create_server_branch()

            if self.repo.active_branch is not branch_name:
                self.add_and_commit_and_push()
                self.repo.git.checkout(branch_name)

        else:
            logger.critical('Could not load repository at {} :('.format(repo_path))
            raise Exception("Could not load repository at {}".format(repo_path))

    def desc_commit(self, count: int = COMMITS_TO_PRINT):

        # create list of commits then print some of them to stdout
        commits = list(self.repo.iter_commits(self.branch_name))[:count]
        for commit in commits:
            logger.opt(raw=True).trace('----\n')
            logger.opt(raw=True).trace(str(commit.hexsha) + "\n")
            logger.opt(raw=True).trace("\"{}\" by {} ({})\n".format(commit.summary,
                                                                    commit.author.name,
                                                                    commit.author.email))
            logger.opt(raw=True).trace(str(commit.authored_datetime) + "\n")
            logger.opt(raw=True).trace(
                str("count: {} and size: {}\n".format(commit.count(), commit.size)))

    def desc_repository(self):
        logger.trace('Repo description: {}'.format(self.repo.description))
        logger.trace(self.repo.references)
        logger.trace('Repo active branch is {}'.format(self.repo.active_branch))
        for remote in self.repo.remotes:
            logger.trace('Remote named "{}" with URL "{}"'.format(remote, remote.url))
        logger.trace('Last commit for repo is {}.'.format(str(self.repo.head.commit.hexsha)))

    def create_server_branch(self):
        logger.info(f"Creating new branch {self.branch_name}")
        new_branch = self.repo.create_head(self.branch_name)
        new_branch.checkout()
        self.repo.git.push('--set-upstream', 'origin', new_branch)

    def add_and_commit_and_push(self):
        if self.repo.is_dirty(untracked_files=True):
            logger.warning("Git repo is dirty. Running commit")
            self.repo.git.add(all=True)
            self.repo.git.commit('-m', 'Auto commit')
            self.desc_commit(1)
            self.repo.git.push()
            logger.info("Auto commit and push completed.")
        else:
            logger.warning("Git repo is clean")
            return


if __name__ == "__main__":
    # 移除內建預設 logger
    logger.remove()

    # 加入寫檔logger
    #logger.add("google_trends.log", rotation="100 KB", level="TRACE", backtrace=True, diagnose=True)

    # 加入顯示在 terminal 的自定義 logger
    logger.add(sys.stdout, level="TRACE", backtrace=True, diagnose=True)
    GitCommand()
