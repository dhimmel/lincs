#!/bin/bash

if [ ! -f l1000_n1328098x22268.gctx ]; then
  echo "Downloading D-GEX gctx"
  URL=https://cbcl.ics.uci.edu/public_data/D-GEX/l1000_n1328098x22268.gctx
  wget $URL
fi

if [ ! -f modzs.gctx ]; then
  echo "Downloading modzs.gctx"
  URL=https://ndownloader.figshare.com/files/5905200
  wget --output-document=modzs.gctx $URL
fi

