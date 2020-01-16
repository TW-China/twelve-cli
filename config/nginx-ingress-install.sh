# install helm
curl https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | bash
helm repo add stable https://kubernetes-charts.storage.googleapis.com/

# install nginx
helm install nginx-ingress stable/nginx-ingress --version 1.28.0

# install cert-manager

kubectl apply --validate=false -f https://raw.githubusercontent.com/jetstack/cert-manager/release-0.12/deploy/manifests/00-crds.yaml
kubectl create namespace cert-manager
helm repo add jetstack https://charts.jetstack.io
helm repo update
helm install --name cert-manager --namespace cert-manager --version v0.12.0 jetstack/cert-manager

# install issuer
kubectl apply -f issuer.yaml
