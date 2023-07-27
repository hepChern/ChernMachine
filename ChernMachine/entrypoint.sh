#!/bin/bash
echo "New environment"
celery -q --workdir=/Users/zhaomr/workdir/Chern/ChernMachine/ChernMachine/.. -A ChernMachine.server.celeryapp worker --loglevel=info
