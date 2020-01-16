import os
import sys
from pprint import pprint

from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend as crypto_default_backend
from cryptography.hazmat.primitives import serialization
import subprocess
import time
from fabric import Connection
from paramiko import AuthenticationException


class Cluster:
    state: str

    def __init__(self, state=None):
        state = os.environ.get("KOPS_STATE_STORE", None) if state is None else state
        if state is None:
            exit("state not set, please specific state via '--state' or set environment variable KOPS_STATE_STORE")
        self.state = state

    def new(self, name):
        pass

        # init certificate folder for cluster
        cluster_path = os.path.join(os.getcwd(), "certificates", name)
        private_key_path = os.path.join(cluster_path, "id_rsa")
        public_key_path = os.path.join(cluster_path, "id_rsa.pub")

        if not os.path.exists(cluster_path):
            os.mkdir(cluster_path)

            # init ssh key

            key = rsa.generate_private_key(
                backend=crypto_default_backend(), public_exponent=65537, key_size=2048)
            private_key = key.private_bytes(
                crypto_serialization.Encoding.PEM, crypto_serialization.PrivateFormat.TraditionalOpenSSL,
                crypto_serialization.NoEncryption())
            public_key = key.public_key().public_bytes(
                crypto_serialization.Encoding.OpenSSH, crypto_serialization.PublicFormat.OpenSSH)

            with open(private_key_path, 'wb') as content_file:
                # os.chmod(private_key_path, 600)
                content_file.write(private_key)
            with open(public_key_path, 'wb') as content_file:
                content_file.write(public_key)

        # create cluster with kops
        kops_command = f"kops create cluster --ssh-public-key {public_key_path} --state={self.state} --zones=us-east-1b {name}"
        process = subprocess.Popen(kops_command.split(" "), stdout=subprocess.PIPE)
        output_payload = ""
        while True:
            output = process.stdout.readline()
            if not output:
                break
            if output:
                output_payload += str(output.strip())
        rc = process.poll()
        if rc != 0:
            exit(f"command '{kops_command}' get non-zero return {rc} \n log: \n {output_payload}")

        kops_update_command = f"kops update cluster --state={self.state} {name} --yes"

        process = subprocess.Popen(kops_update_command.split(" "), stdout=subprocess.PIPE)
        output_payload = ""
        while True:
            output = process.stdout.readline()
            if not output:
                break
            if output:
                output_payload += str(output.strip())
        rc = process.poll()
        if rc != 0:
            exit(f"command '{kops_update_command}' get non-zero return {rc}\n log: \n {output_payload}")

        # validate cluster status

        kops_validate_command = f"kops validate cluster --state={self.state} {name}"
        while True:

            process = subprocess.Popen(kops_validate_command.split(" "), stdout=subprocess.PIPE)
            stdout = process.communicate()[0]
            rc = process.poll()
            if rc == 0:
                break
            else:
                stdout = str(stdout)
                if r"dns\tapiserver\tValidation Failed" in stdout:
                    print(f"validate get return code: {rc}: dns not ready, please wait 5-10 min")
                time.sleep(10)

        self.init(name)

    def init(self, name):
        try:
            # init certificate folder for cluster
            cluster_path = os.path.join(os.getcwd(), "certificates", name)
            private_key_path = os.path.join(cluster_path, "id_rsa")
            public_key_path = os.path.join(cluster_path, "id_rsa.pub")

            # ssh into cluster
            master_api_url = f"api.{name}"

            # private_key_path = "certificates/test.12.3min.work/id_rsa"
            # master_api_url = f"api.test.12.3min.work"
            print(master_api_url)
            print(private_key_path)
            pk = ""
            with open(private_key_path, "rb") as fs:
                pemlines = fs.read()
                pk = serialization.load_pem_private_key(pemlines, None, crypto_default_backend())
            print(f"connecting to master {master_api_url}...")

            conn = Connection(f"{master_api_url}", user="admin", port=22, connect_kwargs={
                "key_filename": private_key_path
                # "pkey": pk
            })


            # install helm
            print(f"install helm...")
            ret = conn.run("curl https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | bash")
            print(f"add helm repo...")
            ret = conn.run("helm repo add stable https://kubernetes-charts.storage.googleapis.com/")
            # install nginx
            print(f"install nginx...")
            ret = conn.run("helm install nginx-ingress stable/nginx-ingress --version 1.28.0")
            # install cert-manager
            print(f"install cert-manager")
            ret = conn.run("kubectl create namespace cert-manager")
            ret = conn.run("kubectl apply --validate=false -f https://raw.githubusercontent.com/jetstack/cert-manager/release-0.12/deploy/manifests/00-crds.yaml")
            ret = conn.run("helm repo add jetstack https://charts.jetstack.io")
            ret = conn.run("helm repo update")
            ret = conn.run("helm install cert-manager --namespace cert-manager --version v0.12.0 jetstack/cert-manager")



            # install registry

            print("init docker registry...")
            conn.run("export SHA=$(head -c 16 /dev/urandom | shasum | cut -d " " -f 1)")
            conn.run("export USER=admin")
            conn.run("echo $USER > registry-creds.txt")
            conn.run("echo $SHA >> registry-creds.txt")
            conn.run("sudo docker run --entrypoint htpasswd registry:2 -Bbn admin $(cat ./registry-creds.txt) > ./htpasswd")
            conn.run("helm install private-registry  stable/docker-registry --namespace default --set persistence.enabled=false --set secrets.htpasswd=$(cat ./htpasswd)")

            conn.put("config/registry-ingress.yaml", "/home/admin/upload-registry-ingress.yaml")
            conn.run("kubectl apply -f /home/admin/upload-registry-ingress.yaml")
            # install jenkins
            print("install jenkins...")
            conn.run("helm install jenkins stable/jenkins")
            conn.put("config/Jenkins/Jenkins-Ingress.yaml", "/home/admin/upload-Jenkins-Ingress.yaml")
            conn.run("kubectl apply -f /home/admin/upload-Jenkins-Ingress.yaml")

            # initial cluster-issuer
            print("install cluster issuer")
            conn.put("config/issuer.yaml", "/home/admin/upload-issuer.yaml")
            ret = conn.run("kubectl apply -f /home/admin/upload-issuer.yaml")
        except AuthenticationException as e:
            pprint(type(e))
            pprint(e)

    def destroy(self, name):
        pass

    def list(self):
        pass
