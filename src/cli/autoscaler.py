"""
Autoscaler interface.
"""


from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter


def cli() -> None:
    """
    Set up the CLI for autoscaler.
    """
    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        description=__doc__
    )

    parser.add_argument(
        '-d', '--daemon', action='store_true', default=False,
        help='Start the autoscaling daemon. By default, this tool is a minimal client.'
    )

    parser.add_argument(
        '-c', '--config', type=str, default='/etc/autoscaler/autoscale.conf',
        help='Configuration file to use.'
    )

    args = parser.parse_args()


if __name__ == '__main__':
    cli()
