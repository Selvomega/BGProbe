import os

def gcloud_get_instance_ip(instance_name, region="us-west2-b"):
    """
    Get the external IP of a gcloud instance with given instance name.
    When zone is NOT specified, we will use a default one.
    """
    cmd = f"gcloud compute instances describe {instance_name} --zone={region} --format=\"get(networkInterfaces[0].accessConfigs[0].natIP)\""
    external_ip = os.popen(cmd).read().strip()
    return external_ip
