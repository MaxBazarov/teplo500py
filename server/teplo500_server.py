import sys

sys.path.insert(1, "/Users/baza/Github/teplo500py/lib")
from teplo500_cmd import cmd_app

app = cmd_app.CmdApp()
if( not app.init()):
	log_error('Can not initiate app')
	exit(-1)

if( not app.parse_cmd_line() ):
	exit -1;

app.run_server()
