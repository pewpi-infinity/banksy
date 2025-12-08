#!/bin/bash
cd /mongoose.os

while true; do
    sleep 300   # check every 5 minutes
    if git status --porcelain infinity_research_output/ | grep -q "^??\|M"; then
        git add infinity_research_output/
        COUNT=$(ls infinity_research_output/*.json 2>/dev/null | wc -l)
        git commit -m "∞ Auto-commit research – \( COUNT files total – \)(date '+%Y-%m-%d %H:%M')"
        git push origin main
        echo "∞ Auto-pushed new research files"
    fi
done
