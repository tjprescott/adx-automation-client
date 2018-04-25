import sys
import shlex
import json
from typing import Callable
from subprocess import check_output, CalledProcessError, STDOUT

import colorama

import a01.cli
from a01.common import DROID_CONTAINER_REGISTRY, IS_WINDOWS
from a01.communication import session


@a01.cli.cmd('check', desc='Examine the current settings and environment.')
def check_environment():
    result = True
    result &= verify_item('Azure CLI',
                          'az --version')
    result &= verify_item('Azure CLI login',
                          'az account show')
    result &= verify_item('Azure CLI subscription',
                          'az account set -s 6b085460-5f21-477e-ba44-1035046e9101',
                          'The current az login failed to sign in '
                          '6b085460-5f21-477e-ba44-1035046e9101 subscription')

    sys.exit(0 if result else 1)


def verify_item(name: str, command: str, hint: str = None, validate_fn: Callable[[str], None] = lambda _: None) -> bool:
    import requests
    try:
        sys.stderr.write(f'Validating {name} ... ')
        sys.stderr.flush()

        output = check_output(shlex.split(command, posix=not IS_WINDOWS), stderr=STDOUT, shell=IS_WINDOWS).decode(
            'utf-8')
        validate_fn(output)

        sys.stderr.write(colorama.Fore.GREEN + 'ok\n' + colorama.Fore.RESET)
        sys.stderr.flush()

        return True
    except (CalledProcessError, ValueError, requests.HTTPError):
        sys.stderr.write(colorama.Fore.RED + 'failed\n' + colorama.Fore.RESET)
        if hint:
            sys.stderr.write(colorama.Fore.YELLOW + hint + '\n' + colorama.Fore.RESET)

        sys.stderr.flush()
        return False


def _check_task_store_healthy(store_ip: str) -> None:
    resp = session.get(f'http://{store_ip}/healthy')
    resp.raise_for_status()
    if json.loads(resp.content.decode('utf-8'))['status'] != 'healthy':
        raise ValueError()
