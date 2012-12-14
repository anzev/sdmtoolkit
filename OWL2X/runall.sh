#!/bin/sh
java -jar owl2x.jar segs short out ~/diploma/bank.tab ~/diploma/geography.owl ~/diploma/banking_services.owl ~/diploma/occupation.owl
cp out/ont ~/psegs_local/downloads_bank/
cp out/g2ont ~/psegs_local/downloads_bank/
cd ~/psegs_local/
C_source/qq.exe work_dir/bank.config
cd ~/workspace/ijs/OWL2X
python scripts/results.py out ~/psegs_local/work_dir/bank.0.fisher.html
