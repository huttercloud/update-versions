#!/usr/bin/env python3

"""
    retrieve current versions and replace lines in specified files with them
"""

from dataclasses import dataclass
import requests
import click
import logging
from typing import Dict, List
import re

# setup logging
logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.INFO)

# versions to retrieve from whattheversion api
VERSIONS=dict(
    NZBTOMEDIA=dict(
        type='git',
        repository='https://github.com/clinton-hall/nzbToMedia.git',
        regexp='^[0-9]+\.?[0-9]+\.?[0-9]+$',
    ),
    EXTERNALDNS=dict(
        type='docker',
        registry='k8s.gcr.io',
        repository='external-dns/external-dns',
        regexp='^v[0-9]+\.?[0-9]+\.?[0-9]+$',
    ),
    PIHOLE=dict(
        type='docker',
        registry='registry.hub.docker.com',
        repository='pihole/pihole',
        regexp='^[0-9]{4}\.[0-9]{1,2}\.[0-9]{1,2}$',
    ),
    WIREGUARD=dict(
        type='docker',
        registry='registry.hub.docker.com',
        repository='linuxserver/wireguard',
        regexp='^[0-9]+\.?[0-9]+\.?[0-9]+$',
    ),
    UNIFICONTROLLER=dict(
        type='docker',
        registry='registry.hub.docker.com',
        repository='linuxserver/unifi-controller',
        regexp='^[0-9]+\.?[0-9]+\.?[0-9]+$',
    ),
    BAZARR=dict(
        type='docker',
        registry='registry.hub.docker.com',
        repository='linuxserver/bazarr',
        regexp='^[0-9]+\.?[0-9]+\.?[0-9]+$',
    ),
    NZBHYDRA2=dict(
        type='docker',
        registry='registry.hub.docker.com',
        repository='linuxserver/nzbhydra2',
        regexp='^[0-9]+\.?[0-9]+\.?[0-9]+$',
    ),
    RADARR=dict(
        type='docker',
        registry='registry.hub.docker.com',
        repository='linuxserver/radarr',
        regexp='^[0-9]+\.?[0-9]+\.?[0-9]+$',
    ),
    SABNZBD=dict(
        type='docker',
        registry='registry.hub.docker.com',
        repository='linuxserver/sabnzbd',
        regexp='^[0-9]+\.?[0-9]+\.?[0-9]+$',
    ),
    SONARR=dict(
        type='docker',
        registry='registry.hub.docker.com',
        repository='linuxserver/sonarr',
        regexp='^[0-9]+\.?[0-9]+\.?[0-9]+$',
    ),
    OAUTH2PROXY=dict(
        type='docker',
        registry='quay.io',
        repository='oauth2-proxy/oauth2-proxy',
        regexp='^v[0-9]+\.?[0-9]+\.?[0-9]+$',
    ),
    FILEBROWSER=dict(
        type='docker',
        registry='registry.hub.docker.com',
        repository='filebrowser/filebrowser',
        regexp='^v[0-9]+\.?[0-9]+\.?[0-9]+$',
    ),
    EXTERNALSECRETS=dict(
        type='helm',
        registry='https://charts.external-secrets.io',
        chart='external-secrets',
        regexp='^[0-9]+\.?[0-9]+\.?[0-9]+$',
    ),
    ARGOCD=dict(
        type='helm',
        registry='https://argoproj.github.io/argo-helm',
        chart='argo-cd',
        regexp='^[0-9]+\.?[0-9]+\.?[0-9]+$',
    ),
    PROMETHEUS=dict(
        type='helm',
        registry='https://prometheus-community.github.io/helm-charts',
        chart='prometheus',
        regexp='^[0-9]+\.?[0-9]+\.?[0-9]+$',
    ),
    GRAFANA=dict(
        type='helm',
        registry='https://grafana.github.io/helm-charts',
        chart='grafana',
        regexp='^[0-9]+\.?[0-9]+\.?[0-9]+$',
    ),
    LOKI=dict(
        type='helm',
        registry='https://grafana.github.io/helm-charts',
        chart='loki',
        regexp='^[0-9]+\.?[0-9]+\.?[0-9]+$',
    ),
    PROMTAIL=dict(
        type='helm',
        registry='https://grafana.github.io/helm-charts',
        chart='promtail',
        regexp='^[0-9]+\.?[0-9]+\.?[0-9]+$',
    ),
    TEMPO=dict(
        type='helm',
        registry='https://grafana.github.io/helm-charts',
        chart='tempo',
        regexp='^[0-9]+\.?[0-9]+\.?[0-9]+$',
    ),
    TAUTULLI=dict(
        type='docker',
        registry='ghcr.io',
        repository='tautulli/tautulli',
        regexp='^v[0-9]+\.?[0-9]+\.?[0-9]+$',
    ),
    OVERSEERR=dict(
        type='docker',
        registry='registry.hub.docker.com',
        repository='linuxserver/overseerr',
        regexp='^[0-9]+\.?[0-9]+\.?[0-9]+$',
    ),
    CALIBRE=dict(
        type='docker',
        registry='registry.hub.docker.com',
        repository='linuxserver/calibre',
        regexp='^[0-9]+\.?[0-9]+\.?[0-9]+$',
    ),
    CALIBREWEB=dict(
        type='docker',
        registry='registry.hub.docker.com',
        repository='linuxserver/calibre-web',
        regexp='^[0-9]+\.?[0-9]+\.?[0-9]+$',
    ),
    READARR=dict(
        type='docker',
        registry='registry.hub.docker.com',
        repository='linuxserver/readarr',
        regexp='^[0-9]+\.?[0-9]+\.?[0-9]+-develop$', # only develop versions are currently available
    ),
    PROWLARR=dict(
        type='docker',
        registry='registry.hub.docker.com',
        repository='linuxserver/prowlarr',
        regexp='^[0-9]+\.?[0-9]+\.?[0-9]+$',
    ),
    JENKINS=dict(
        type='helm',
        registry='https://charts.jenkins.io',
        chart='jenkins',
        regexp='^[0-9]+\.?[0-9]+\.?[0-9]+$',
    ),
)
def retrieve_versions(endpoint: str) -> Dict[str, str]:
    """
    retrieve specified versions in VERSIONS and return the found values
    :param url:
    :return:
    """

    versions = dict()

    for k, v in VERSIONS.items():
        try:
            url = f'{endpoint}/{v.get("type")}'
            payload = v
            payload.pop('type')
            r = requests.post(url=url, json=payload)
            r.raise_for_status()
            versions[k] = r.json()['version']
        except Exception as e:
            logging.warning(e)

    return versions

@dataclass
class Replacement:
    pattern: re.Pattern
    version: str

def prepare_replacements(replacements: tuple, versions: Dict[str, str]) -> List[Replacement]:
    """
    parse the given replacements, ensures they are valid and return the sanitized list
    :param replacements:
    :param versions:
    :return:
    """

    validated_replacements = []
    for r in replacements:
        # compile regular expression pattern
        try:
            pattern = re.compile((r[0].replace('\'', '')))
        except Exception as e:
            logging.warning(f'Invalid regular expression received: {e}')
            continue

        version = versions.get(r[1])
        if not version:
            logging.warning(f'No version found for {r[1]}. Continue with next entry.')
            continue

        validated_replacements.append(Replacement(
            pattern=pattern,
            version=version

        ))

    return validated_replacements

@click.command()
@click.option('--whattheversion-endpoint', default='https://whattheversion.hutter.cloud/api')
@click.option('--file', type=click.Path(exists=True), multiple=True, required=True)
@click.option("--replace", "-r", type=(str, str), multiple=True, required=True)
def update_versions(whattheversion_endpoint: str, file: tuple, replace: tuple):

    logging.info(f'Retrieve versions from {whattheversion_endpoint}')
    versions = retrieve_versions(endpoint=whattheversion_endpoint)
    logging.info(f'Found the following versions: {versions}')

    logging.info(f'Prepare regular expressions specified with --replace')
    replacements = prepare_replacements(replacements=replace, versions=versions)
    logging.info(f'Found the follwoing replacements: {replacements}')

    for fi in file:
        logging.info(f'Search and replace in file {fi}')
        # load all lines from file to run search and replace over them
        # file will be opened again for overwriting.

        file_contents = []
        with open(fi, 'r') as f:
            file_contents = f.readlines()

        for i in range(len(file_contents)):
            for r in replacements:
                match = re.match(r.pattern, file_contents[i])
                if match:
                    if len(match.groups()) != 1:
                        logging.warning(f'Found match but no or to many groups for replacement!')
                        continue
                    logging.info(f'Found match for {r.pattern}, replace match with {r.version}')
                    file_contents[i] = f'{file_contents[i][0:match.start(1)]}{r.version}{file_contents[i][match.end(1):]}'

        # write file with updated content
        with open(fi, 'w') as f:
            f.writelines(file_contents)

if __name__ == '__main__':
    update_versions()
