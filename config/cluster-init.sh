# install aws and kops first, and well configured with aws

# let aws route53 take control of your domain
aws route53 create-hosted-zone --name dev.example.com --caller-reference 1

# create a s3 bucket for presistence volume
aws s3 mb s3://clusters.dev.example.com

# create cluster config 
KOPS_STATE_STORE=s3://clusters.dev.example.com kops create cluster --zones=us-east-1c useast1.dev.example.com

# startup cluster
KOPS_STATE_STORE=s3://clusters.dev.example.com kops update cluster useast1.dev.example.com --yes

# wait 1min
sleep 60
kops validate cluster

#  
