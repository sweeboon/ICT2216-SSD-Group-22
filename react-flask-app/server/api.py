import sqlalchemy as sa
import sqlalchemy.orm as so
from api import create_app, db
from api.models import Account

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Account': Account}
