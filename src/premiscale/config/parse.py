"""
Parse a configuration file, or create a default one.
"""


import yamale
import yaml
import logging
import sys

from typing import Tuple
from pathlib import Path
from importlib import resources
from premiscale.config.v1alpha1 import Config


log = logging.getLogger(__name__)


__all__ = [
    'configParse',
    'validate'
]


def configParse(config: str) -> Config:
    """
    Parse a config file and return it as a Config-object. Optionally validate types and structure against the Yamale schema.

    Args:
        config (str): path to the config file.

    Returns:
        Config: The parsed config file.
    """
    # Drop a default config for parsing.
    if not Path(config).exists():
        makeDefaultConfig(config)

    with open(config, 'r', encoding='utf-8') as f:
        try:
            _loaded_config = yaml.safe_load(
                f.read().rstrip()
            )

            _config = Config.from_dict(_loaded_config)

            validate(_loaded_config, version=_config.version)
        except (yaml.YAMLError, KeyError) as e:
            log.error(f'Error parsing config file: {e}')
            sys.exit(1)

    log.debug(f'Successfully parsed config version {_config.version}: {_loaded_config}')

    return _config


def validate(data: dict, version: str = 'v1alpha1', strict: bool = True) -> None:
    """
    Validate users' config files against our schema.

    Args:
        data (dict): config file path/name to validate against the schema.
        version (str): the version of the config file to validate. (default: 'v1alpha1')
        strict (bool): whether or not to use strict mode on yamale. (default: True)
    """
    try:
        with resources.open_text('premiscale.config.schemas', f'schema.{version}.yaml') as schema_f:
            schema = yamale.make_schema(schema_f.name)
    except FileNotFoundError:
        log.error(f'Could not find schema "{schema}" for config version {version}: are you using a supported config version?')
        sys.exit(1)

    try:
        yamale.validate(
            schema,
            data,
            strict=strict
        )
    except ValueError as e:
        log.error(f'Error validating config file: {e}')
        sys.exit(1)


def makeDefaultConfig(path: str | Path, default_config: str | Path = 'default.yaml') -> None:
    """
    Make a default config file if one does not exist.

    Args:
        path (str | Path): The default location to create an autoscale configuration file, if it doesn't exist.
        default_config (str | Path): The default config file to use when creating a new config file. (default: 'default.yaml')
    """
    try:
        if not Path.exists(Path(path).parent):
            Path.mkdir(Path(path).parent, parents=True)

        if not Path(path).exists():
            log.debug(f'Config file at {path} does not exist. Creating default config file.')

            with resources.open_text('premiscale.config', str(default_config)) as default_f, open(str(path), 'x', encoding='utf-8') as f:
                f.write(default_f.read().strip())

            log.debug(f'Successfully created default config file at \'{str(path)}\'')
    except PermissionError:
        log.error(f'premiscale does not have permission to install to {str(Path(path).parent)}, must run as root.')
        sys.exit(1)
