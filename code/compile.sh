#!/bin/bash
###########################################################################
#    Compile.sh
#    ---------------------
#    Date                 : June 2017
#    Copyright            : (C) 2017 by Fran Raga
#    Email                : franka1986 at gmail dot com
###########################################################################
#                                                                         #
#   This program is free software; you can redistribute it and/or modify  #
#   it under the terms of the GNU General Public License as published by  #
#   the Free Software Foundation; either version 2 of the License, or     #
#   (at your option) any later version.                                   #
#                                                                         #
###########################################################################

echo "converting ui files"

pyuic5 --import-from EquirectangularViewer.gui ui/ui_orbitalDialog.ui -o gui/ui_orbitalDialog.py  

echo "converting resources file"

pyrcc5 ui/resources.qrc -o gui/resources_rc.py

