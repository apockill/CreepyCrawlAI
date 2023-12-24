# CreepyCrawlAI
<img align="center" src="https://github.com/apockill/CreepyCrawlAI/workflows/Tests/badge.svg">

Pronounced CreepyCrawl-y. 

## Running the Project
### Installing dependencies
Run the following commands, changing "PLATFORM" and "PYTHON" to be the correct
godot-python distribution for your platform (available under the `addons/pythonscript/`
directory).
```bash
PLATFORM=addons/pythonscript/x11-64
PYTHON=$PLATFORM/bin/python3.7
chmod +x $PYTHON
export LD_PRELOAD=\"$(printf %q "$(realpath $PLATFORM/lib/libpython3.7m.so.1.0)")\"
export LD_PRELOAD=$PLATFORM/lib/libpython3.7m.so.1.0
$PYTHON -m pip install --upgrade pip
$PYTHON -m pip install --upgrade -r requirements.txt
```

Running tests doesn't require installing the testing libraries into the
`pythonscript/` installation. Virtualenv is recommended!
```
pip install -r requirements.txt -r tests/requirements.txt
```

## Running Tests
All tests are under `tests/`. To avoid accidentally running the godot-python 
tests, run 
```
pytests tests/
```