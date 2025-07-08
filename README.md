# Maintainers and Authors

Find the contact details for maintainers and authors of specified projects on PyPi, using PyPi's JSON API.
-----

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Installation

```console
uv tool install maintainers-and-authors
```

## Usage

Project names are intentionally read from stdin.

```console
echo rev-deps | maintainers-and-authors
```

Bash
```console
cat requirements.txt | maintainers-and-authors
```

Cmd.exe
```console
type requirements.txt | maintainers-and-authors
```

## License

`maintainers-and-authors` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
