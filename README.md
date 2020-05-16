# CreepyCrawlAI
Pronounced CreepyCrawl-y. 

## Installing Dependencies
Run the following commands, changing "x11-64-cpython" to be the correct
godot-python distribution for your platform (available under the pythonscript/
directory).

```bash
pip install --upgrade -r requirements.txt --target pythonscript/x11-64-cpython/lib/python3.6/site-packages
```

## Running Tests
All tests are under tests/. To avoid accidentally running the godot-python 
tests, run `pytests tests/`