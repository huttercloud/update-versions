# update-versions

Simple python script to update software versions in terraform files, helm manifests etc by replacing
lines via regular expressions.

current versions are retrieved by querying [https://whattheversion.hutter.cloud/api](https://whattheversion.hutter.cloud)

The versions are stored during script execution with keys like 'PIHOLE' or 'WIREGUARD'

The replace parameter for the script can be added multiple times.
The first part of the parameter is the regular expression to look for in the file, the regular expression requires
one group (e.g. one string in `(` and `)`). Quotes `"` and single quotes `'` need to be escaped with a `\`.

## example query

```bash
./update-versions.py \
    --file locals.tf \
    --replace '\s*?pi_hole_version\s*?=\s+\"(.*?)\"' PIHOLE \
    --replace '\s*?wireguard_version\s*?=\s+\"(.*?)\"' WIREGUARD
```