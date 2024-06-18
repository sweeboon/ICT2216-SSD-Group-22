from api.main import bp
import time 

@bp.route('/time')
def get_current_time():
    return {'time': time.time()}