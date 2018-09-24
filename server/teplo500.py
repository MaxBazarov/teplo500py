
import CmdApp

app = CmdApp.CmdApp()
if( not app.init()):
	log_error('Can not initiate app')
	exit(-1)

if( not app.parse_cmd_line() ):
	exit -1;

app.run_server()
