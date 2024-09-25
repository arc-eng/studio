# Variables
VERSION := $(shell poetry version -s)
IMAGE := arceng/studio

# Phony Targets
.PHONY: docker docker-push

docker:
	docker build --platform linux/amd64 -t $(IMAGE):$(VERSION) .

docker-push: docker
	docker tag $(IMAGE):$(VERSION) $(IMAGE):latest
	docker push $(IMAGE):$(VERSION)
	docker push $(IMAGE):latest