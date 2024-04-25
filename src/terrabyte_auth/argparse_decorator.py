import argparse


def argument(*names_or_flags, **kwargs):
        return names_or_flags, kwargs

def subcommand(*subparser_args, parent: argparse.ArgumentParser):
    def decorator(func):
        parser = parent.add_parser(func.__name__, description=func.__doc__)
        for args, kwargs in subparser_args:
            parser.add_argument(*args, **kwargs)
        parser.set_defaults(func=func)
    return decorator
