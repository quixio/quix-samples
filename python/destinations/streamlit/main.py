import sys
from streamlit import cli as stcli

if __name__ == '__main__':
    sys.argv = ["streamlit", "run", "streamlit_file.py", "--server.port=80"]
    sys.exit(stcli.main())
