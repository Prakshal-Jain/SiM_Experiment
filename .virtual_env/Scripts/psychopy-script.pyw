#!c:\users\innos\sim_experiment\.virtual_env\scripts\pythonw.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'PsychoPy==2021.1.4','gui_scripts','psychopy'
__requires__ = 'PsychoPy==2021.1.4'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('PsychoPy==2021.1.4', 'gui_scripts', 'psychopy')()
    )
