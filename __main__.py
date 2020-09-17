import utils
from app import *
from pathlib import Path

app.jinja_env.globals.update(decrypt_message=utils.decrypt_message)
Path("./database").mkdir(parents=True, exist_ok=True)

if __name__ == '__main__':
    app.run(debug=True)
