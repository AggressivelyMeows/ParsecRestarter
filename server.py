"""
Made by Cerulean#7014 on Discord

GitHub: AggressivelyMeows

** ALWAYS CHECK THE SOURCE CODE @ MY GITHUB **
"""
import sys
import traceback
import os
import ctypes
import flask
import functools
import time
import psutil


debug = 1
if debug:
    def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        sys.exit(1)

PORT = 81
LISTENING = '0.0.0.0'
PARSEC_INSTALL_LOCATION = 'C:\Program Files\Parsec'

# we now have admin rights

def kill_process(process_name):
    return os.system('taskkill /f /im ' + process_name)

def start_parsec():
    return os.system('"' + PARSEC_INSTALL_LOCATION + '\parsecd.exe"')


app = flask.Flask(__name__)

# allows for us to disallow anyone trying to sneek into the program
def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == 'admin' and password == 'password' # CHANGE. CHANGE ASAP

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return flask.Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        auth = flask.request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.route('/restart')
@requires_auth
def app_restart_parsec():
    """
    Kills parsec's daemon and returns a HTTP response
    """
    ext = kill_process('parsecd.exe')

    print('We tried to kill parsec with response:\n', ext)
    error = 'An unknown error has happened. I think you should take a peak at the console for this!'

    if str(ext) == '0':
        # task was successful
        time.sleep(1) # wait for the process to shutdown for real
        test = str(kill_process('parsecd.exe'))
        if test == '128' or test == '0':
            # we killed it
            ext = start_parsec() # now we restart!
            print('Attempting to start Parsec Daemon with exit code: ', ext)
            return flask.render_template('success.html')
        else:
            error = 'Parsec daemon could not be stopped.'

    
    if str(ext) == '128':
        # 404, task not found
        error = 'Parsec was not running at this time. Please try going to /start'

    return flask.render_template('error.html', error = error)

@app.route('/start')
@requires_auth
def app_start_parsec():
    """
    Starts parsec's daemon and returns a HTTP response
    """
    
    ext = start_parsec()

    print('We tried to run parsec with response:\n', ext)
    if str(ext) == '0':
        # task was successful
        return flask.render_template('success.html')

    error = 'An unknown error has happened. I think you should take a peak at the console for this!'

    return flask.render_template('error.html', error = error)

@app.route('/')
def index():
    return flask.render_template('index.html')

if __name__ == '__main__':
    app.run(LISTENING, PORT)
