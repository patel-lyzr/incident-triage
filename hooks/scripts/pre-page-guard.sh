#!/usr/bin/env bash
# Lightweight belt-and-suspenders guard. Real enforcement is the SRS policy +
# compliance.human_in_the_loop; this just annotates the decision log.
read -r _input
echo '{"decision":"allow","systemMessage":"channel post permitted; paging still requires human review"}'
