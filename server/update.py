import sys

sys.path.insert(1, "/Users/baza/Github/teplo500py/lib")
import teplo500_cmd.cmd_app
from teplo500.core import *

app = CmdApp.CmdApp()
if( not app.init()):
	log_error('Can not initiate app')
	exit(-1)

if( not app.parse_cmd_line() ):
	exit -1

app.run_once()

