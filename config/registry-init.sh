export SHA=$(head -c 16 /dev/urandom | shasum | cut -d " " -f 1)
export USER=admin

echo $USER > registry-creds.txt
echo $SHA >> registry-creds.txt

sudo ocker run --entrypoint htpasswd registry:2 -Bbn admin $SHA > ./htpasswd

helm install private-registry  stable/docker-registry \
  --namespace default \
  --set persistence.enabled=false \
  --set secrets.htpasswd=$(cat ./htpasswd)
