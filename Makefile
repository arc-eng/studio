# Variables
VERSION := $(shell poetry version -s)
POSTGRES_PASSWORD := $(shell grep POSTGRES_PASSWORD .env | cut -d '=' -f2)
IMAGE := arceng/studio

# Phony Targets
.PHONY: docker docker-push

docker:
	docker build --platform linux/amd64 -t $(IMAGE):$(VERSION) .

docker-push: docker
	docker tag $(IMAGE):$(VERSION) $(IMAGE):latest
	docker push $(IMAGE):$(VERSION)
	docker push $(IMAGE):latest

create-k8s-secrets:
	kubectl delete secret arcane-studio-secret
	kubectl create secret generic arcane-studio-secret --from-env-file=.env

deploy:
	helm upgrade --install arcane-studio ./helm-chart --set image.tag=$(VERSION) --values values.yaml