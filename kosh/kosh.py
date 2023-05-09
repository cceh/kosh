from configparser import ConfigParser
from importlib import import_module
from logging import basicConfig, getLogger
from multiprocessing import Process
from os import getpid, path
from pathlib import Path
from pkgutil import iter_modules
from queue import Empty, Queue
from signal import pause
from sys import argv, exit
from threading import Thread
from time import sleep

from elasticsearch_dsl import connections
from flask import Flask, cli

from .elastic.index import index
from .utility.defaultconfig import defaultconfig
from .utility.dotdictionary import dotdictionary
from .utility.instance import instance
from .utility.logger import logger


def main() -> None:
    kosh().main()


if __name__ == "__main__":
    main()


class kosh:
    """
    todo: docs
    """

    def __init__(self) -> None:
        """
        todo: docs
        """
        argv.pop(0)

        basicConfig(
            datefmt="%Y-%m-%d %H:%M:%S",
            format="%(asctime)s [%(levelname)s] <%(name)s> %(message)s",
        )

        cli.show_server_banner = lambda *_: None
        getLogger("elasticsearch").disabled = True
        getLogger("werkzeug").disabled = True

    def main(self) -> None:
        """
        todo: docs
        """
        try:
            instance.config = ConfigParser()
            instance.config.read_dict(defaultconfig)
            logger().info("Started kosh with pid %s", getpid())

            root = "{}/{}".format(path.dirname(__file__), "api")
            modules = [i for _, i, _ in iter_modules([root]) if i[0] != ("_")]
            logger().info("Loaded API endpoint modules %s", modules)

            instance.modules = [
                import_module("kosh.api.{}".format(module)).__dict__[module]
                for module in modules
            ]

            for arg in [i for i in argv if i.startswith("--")]:
                try:
                    module = "kosh.param.{}".format(arg[2:])
                    import_module(module).__dict__[arg[2:]](argv)
                except Exception:
                    exit("Invalid parameter or argument to {}".format(arg[2:]))

            config = dotdictionary(instance.config["data"])
            connections.create_connection(hosts=[config.host])
            logger().info("Connecting to Elasticsearch host %s", config.host)

            instance.lexicons = {
                lexicon.uid: lexicon
                for lexicon in index.lookup(config.root, config.spec)
            }

            instance.query_types = [
                query_type
                for query_type in instance.config["query_types"]
                if query_type not in instance.config.defaults()
                and instance.config.getboolean("query_types", query_type)
            ]

            for lexicon in instance.lexicons.values():
                index.update(lexicon)

            self.serve()
            self.watch() if int(config.sync) > 0 else pause()

        except KeyboardInterrupt:
            print("\N{bomb}")
        except Exception as exception:
            logger().exception(exception)
        except SystemExit as exception:
            logger().critical(exception)

        finally:
            logger().info("Stopped kosh with pid %s", getpid())

    def serve(self) -> None:
        """
        todo: docs
        """
        config = dotdictionary(instance.config["api"])
        flask = Flask(config.name, root_path=Path(__file__).parent)
        flask.config["PROPAGATE_EXCEPTIONS"] = True
        flask.url_map.strict_slashes = False

        def specs(lexicon):
            return {
                "properties": [
                    "id",
                    *[i for i in lexicon.schema.mappings.properties],
                ],
                "query_types": instance.query_types,
                "endpoints": {
                    module.__module__.split(".")[-1]: "{}/{}/{}".format(
                        instance.config["api"]["root"],
                        lexicon.uid,
                        module.__module__.split(".")[-1],
                    )
                    for module in instance.modules
                },
                **{
                    key: value
                    for key, value in lexicon.items()
                    if key not in ["files", "pool", "schema", "uid"]
                },
            }

        flask.add_url_rule(
            config.root,
            config.root,
            lambda: {
                "about": {**instance.config["info"]},
                "dicts": {i.uid: specs(i) for i in instance.lexicons.values()},
            },
        )

        flask.add_url_rule(
            "{}/<uid>".format(config.root),
            "{}/<uid>".format(config.root),
            lambda uid: specs(instance.lexicons[uid]),
        )

        for lexicon in instance.lexicons.values():
            for module in instance.modules:
                module(lexicon).deploy(flask)

        class process(Process):
            def run(self) -> None:
                flask.run(host=config.host, port=config.port)
                logger().info("Listening on %s:%s", config.host, config.port)

        try:
            instance.server.terminate()
            instance.server.join()
        except Exception:
            pass

        instance.server = process(daemon=True, name="server")
        instance.server.start()

    def watch(self) -> None:
        """
        todo: docs
        """
        config = dotdictionary(instance.config["data"])
        queue = Queue()

        def watcher(lexicon):
            instance.lexicons[lexicon.uid] = lexicon
            index.update(lexicon)
            self.serve()

        class thread(Thread):
            def run(self) -> None:
                logger().info("Starting data sync in %s", config.root)
                for lexicon in index.notify(config.root, config.spec):
                    queue.put(lexicon)

        thread(daemon=True, name="update").start()

        while True:
            try:
                for lexicon in queue.get(False)():
                    watcher(lexicon)
            except Empty:
                sleep(int(config.sync))
