# terrapi

The [terrabyte](https://docs.terrabyte.lrz.de) Client library `terrapi` is a small command line interface to help users interact with terrabyte APIs. It encompasses support for user authentication via 2FA login and caches the resulting auth-tokens for use in further api calls. 

## Installation

### Activating terrapi on terrabyte from lrz module system

`terrapi` is available via the [terrabyte module system](https://docs.terrabyte.lrz.de/software/modules/). Simply run:

```bash
# consider adding the module use line to your ~/.bashrc to always make terrabyte modules available 
module use /dss/dsstbyfs01/pn56su/pn56su-dss-0020/usr/share/modules/files/
module load terrapi
```

Aferwards the terrapi cli command is active in your shell.

### Manual installation

```bash
pip install git+https://github.com/DLR-terrabyte/terrapi.git@latest-release
```

### Activate shell autocomplete

If you are using the bash, fish or zsh shell you can activate bash autocomplete of the terrapi cli by running one of the following commands (or adding it to your shell startup file or venv postactivate file to activate by default). If you are using bash shell and loading terrapi via the terrabyte modul system autocomplete is activated by default.

**bash** (add to ~/.bashrc) :
```bash
eval "$(_TERRAPI_COMPLETE=bash_source terrapi)"
```

**zsh** (add to ~/.zshrc):

```bash
eval "$(_TERRAPI_COMPLETE=zsh_source terrapi)"
```

**fish** (add to ~/.config/fish/completions/terrapi.fish)
```bash
_TERRAPI_COMPLETE=zsh_source terrapi > ~/.config/fish/completions/terrapi.fish
```
## Usage

```
Usage: terrapi [OPTIONS] COMMAND [ARGS]...
```

Please find more information at the terrabyte documentation site: https://docs.terrabyte.lrz.de/software/tools/terrapi/

The following sub-commands are available: `stac`

### STAC API Usage

Following commands are available for `terrapi stac`
- `login` to interactively login into terrabyte via 2FA to obtain a refresh token for the API
- `auth` to print the single use auth token needed to directly interact with the private STAC API
- `collection` to interact with STAC collections
- `item` to interact with STAC items
