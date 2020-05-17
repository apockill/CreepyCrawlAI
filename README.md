# CreepyCrawlAI
<img align="center" src="https://github.com/apockill/CreepyCrawlAI/workflows/Tests/badge.svg">

Pronounced CreepyCrawl-y. 

## Installing Dependencies
Run the following commands, changing "x11-64-cpython" to be the correct
godot-python distribution for your platform (available under the `pythonscript/`
directory).

### For running the project:
```bash
pip install --upgrade -r requirements.txt --target pythonscript/x11-64-cpython/lib/python3.6/site-packages
```

### For tests:
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