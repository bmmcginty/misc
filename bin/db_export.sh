#!/bin/bash
set -e
cd ~/run
for db in $@
do
echo "\t
\a
select row_to_json(r) from (select attname as name, format_type(atttypid, atttypmod) as type from pg_attribute where attrelid = '${db}'::regclass and attnum > 0 and NOT attisdropped order by attnum) as r;
" | psql -q > data/db/${db}.schema.new
mv data/db/${db}.schema.new data/db/${db}.schema
echo "\t
\a
SELECT row_to_json(r) FROM ${db} AS r;
" | psql -q | gzip -c > data/db/${db}.json.gz.new
mv data/db/${db}.json.gz.new data/db/${db}.json.gz
done
