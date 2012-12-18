#!/usr/bin/bash

# testing
getquote -t myportfolio
dbselect -t myportfolio regular new_xray sec_xray_id sec_prop_value
dbselect -ti myportfolio matched -lsec_prop_name -msec_prop_name new_xray sec_xray_id security_property sec_prop_id
join-files -t security_xray
create-csv -f security_updates[4].out
insert-csv -f security_updates[2].csv myportfolio