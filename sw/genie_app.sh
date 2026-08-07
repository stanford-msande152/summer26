#!/bin/sh

# Place the GeNIe exeutable in the list of launchable Mac appllications
# Do this after both Genie and Wine are installed
#      JMA Aug 2026

GENIE=$(find ~/.wine -iname "genie.exe" 2>/dev/null | head -1); 
WINE=$(which wine); 
echo "Found $GENIE"
echo "Found $WINE"
# osacompile -o /Applications/GeNIe.app -e "do shell script "$WINE '$GENIE' # > /dev/null 2>&1 &"" && echo "✅ Done — found GeNIe at: $GENIE"
osacompile -o /Applications/GeNIe.app -e 'do shell script "'$WINE" '"$GENIE"'"'"' # > /dev/null 2>&1 &"" && echo "✅ Done — found GeNIe at: $GENIE"