#!/bin/sh

echo $0 > test.out       # path to this file
echo $1 >> test.out
echo $2 >> test.out      # sys.argv[1]; api_url
echo $3 >> test.out      # sys.argv[2]; simulation_id
echo $4 >> test.out      # sys.argv[3]; owner_id
echo $5 >> test.out      # sys.argv[4]; session_id
echo $6 >> test.out      # sys.argv[5]: algorithm name
python $1/$6.py $2 $3 $4 $5 $6