#!/bin/bash

PROGRAM="./src/pakbon-ld.py"
INPUT_PATH="./if/"
OUTPUT_PATH="./ofl/"
FORMAT="turtle"
FORMAT_EXT="ttl"
NAMESPACE="http://pakbon-ld.spider.d2s.labs.vu.nl"
ALIGN="local"
ENDPOINT="${NAMESPACE}/sparql/"
GRAPHS=""

for FILE in $(ls "${INPUT_PATH}/"*.xml)
do
	echo "processing ${FILE}"

	GRAPHS=$(ls -d "${OUTPUT_PATH}"/*.$FORMAT_EXT)

	python3.5 "${PROGRAM}" \
		-i "${FILE}"\
		-d "${NAMESPACE}"\
		-o "${OUTPUT_PATH}/$(basename ${FILE%.xml})"\
		-f $FORMAT\
		--align=$ALIGN\
		--align_with="${GRAPHS//[$'\n']/ }"\
		--endpoint="${ENDPOINT}"\
		--enable_georesolver\
		--ignore_version
done
