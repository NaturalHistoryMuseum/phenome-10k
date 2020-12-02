node node &
flask run &
function end_jobs(){
	kill %2
	kill %1
}
trap end_jobs SIGINT
wait
