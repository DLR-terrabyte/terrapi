#!/bin/bash
#latest md-click has a bug  that crashes if there are no options for inital command. fixed by using fixed branch that has not been merged
# git clone https://github.com/kid-116/md-click.git
# cd md-click/
# git checkout support-arguments
# git pull
# pip install --no-build-isolation . #no idea why we need the no-build-isolation but  python 3.12 fails without it
cd $(dirname $0)


#clean up to make sure there are no remnants
rm docs/raw/*md
mdclick dumps --baseModule=terrapi.cli.terrapi_cli --baseCommand=terrapi --docsPath=docs/raw
cd docs/raw

#patch documenation that make issues in docusaurus
sed -i 's#<click.types.File .*>#File#g' *md
sed -i 's#<ConsoleStream name.*stdout.*>#stdout#g' *md
sed -i 's#<#\\<#g' *md
sed -i 's#>#\\>#g' *md 

copyAddingHeader (){
echo "---
id: $3
title: $3
description: terrapi command line library documentation - $4 subcommand
---">$2
cat $1>>$2
}


move2Subfolders () {
    local start=$1
    local folder=$2
    local md
    local sub  
    mkdir -p $folder/$start
    for md in $(ls ${start}-*.md)
    do
       #echo doing $md 
       sub=${md/${start}-}
       sub=${sub/.md/}
       #echo "sub is: $sub"
       ls ${sub}-*.md 2>/dev/null >/dev/null
       if [ "$?" -eq "0" ]
       then
          #echo calling move2Subfolders $sub ${folder}/${start}       
          move2Subfolders $sub ${folder}/${start}
          copyAddingHeader $md ${folder}/${start}/${sub}/${sub}.md ${sub}
        else
           #final command
            copyAddingHeader $md $folder/$start/${sub}.md $sub $start
        fi 
    done

}
move2Subfolders terrapi ../docusaurus
cp terrapi.md ../docusaurus/terrapi