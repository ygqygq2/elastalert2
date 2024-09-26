#!/bin/sh
set -e

# 如果没有传递参数，则执行默认命令
if [ "$#" -eq 0 ]; then
  elastalert-create-index --config /opt/elastalert/config.yaml
  elastalert --config /opt/elastalert/config.yaml
else
  # 否则执行用户指定的命令
  exec "$@"
fi
