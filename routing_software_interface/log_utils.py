import os

def collect_log_frr() -> str:
    """
    Collect the log content of the FRR instance.
    Must execute the file with sudo command.
    """
    with open("/var/log/frr/bgpd.log", 'r') as file:
        content = file.read()
    return content

def clear_log_frr():
    """
    Clear the log content of the FRR instance.
    """
    with open("/var/log/frr/bgpd.log", 'w') as file:
        file.write('')
    return
