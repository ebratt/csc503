#!/bin/sh
#echo $0 > test.out       # path to this file
#echo $1 >> test.out      # module folder
#echo $2 >> test.out      # sys.argv[1]; log_api_url
#echo $3 >> test.out      # sys.argv[2]; plot_api_url
#echo $4 >> test.out      # sys.argv[3]; temp_url
#echo $5 >> test.out      # sys.argv[4]; simulation_id
#echo $6 >> test.out      # sys.argv[5]; user_id
#python $1/floating_point_add.py $2 $3 $4 $5 $6

echo $0 > test.out       # path to this file
echo $1 >> test.out
echo $2 >> test.out      # sys.argv[0]; api_url
echo $3 >> test.out      # sys.argv[1]; simulation_id
echo $4 >> test.out      # sys.argv[2]; owner_id
echo $5 >> test.out      # sys.argv[3]; session_id
python $1/floating_point_add.py $2 $3 $4 $5
