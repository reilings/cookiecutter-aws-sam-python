BASE := $(shell /bin/pwd)

################# 
#  Python vars	#
################# 

SERVICE = {{ cookiecutter.project_module_slug }}

DOCKER = 1

#######################
# CloudFormation vars #
#######################

BUCKET ?= bucket_not_defined

REGION = 'us-east-1'

STACK = {{ cookiecutter.project_slug }}

############# 
#  SAM vars	#
############# 

NETWORK = ""

target:
	$(info ${HELP_MESSAGE})
	@exit 0

clean: ##=> Deletes current build environment and latest build
	$(info [*] Who needs all that anyway? Destroying environment....)
	rm -rf ./build
	rm -rf ./${SERVICE}.zip

all: clean build

install: _install_packages _install_dev_packages

shell: 
	@pipenv shell

package: _check_service_definition ##=> Builds package using Docker Lambda container
ifeq ($(DOCKER),1)
	$(info [*] Cleaning up local dev/builds before build task...)
	@$(MAKE) clean SERVICE="${SERVICE}"
	$(info [+] Packaging service '$(SERVICE)' using Docker Lambda -- This may take a while...)
	docker run -v $$PWD:/var/task -it lambci/lambda:build-python3.6 /bin/bash -c 'make _package SERVICE="${SERVICE}"'
else
	$(info [*] Cleaning up local builds before build task...)
	@$(MAKE) clean SERVICE="${SERVICE}"
	$(info [+] Packaging service '$(SERVICE)' -- This may take a while...)
	@$(MAKE) _package SERVICE="${SERVICE}"
endif

build: _check_service_definition _clone_service_to_build ##=> Same as package except that we don't create a ZIP
	@$(MAKE) _install_deps SERVICE="${SERVICE}"

run: ##=> Run SAM Local API GW and can optionally run new containers connected to a defined network
	@test -z ${NETWORK} \
		&& sam local start-api \
		|| sam local start-api --docker-network ${NETWORK}

test: ##=> Run pytest
	@pipenv run python -m pytest --cov . --cov-report term-missing tests/ -v

upload: _check_package_zip
	@aws cloudformation package --template-file template.yaml --output-template-file packaged.yaml --s3-bucket ${BUCKET}

deploy: _check_package_yaml
	@aws cloudformation package --template-file packaged.yaml --stack-name ${STACK} --capabilities CAPBILITY_IAM --region ${REGION}

############# 
#  Helpers  #
############# 

_install_packages:
	$(info [*] Install required packages...)
	@pipenv --three install

_install_dev_packages:
	$(info [*] Install required dev-packages...)
	@pipenv install -d

_check_package_zip:
	ifeq ($(wildcard $(SERVICE).zip),)
		$(error [!] '$(SERVICE).zip' package doesn't exist. Run 'make package' first)
	endif

_check_package_yaml:
	ifeq ($(wildcard packaged.yaml),)
		$(error[!] 'packaged.yaml' file doesn't exist. Run 'make upload' first)
	endif

_check_service_definition:
	$(info [*] Checking whether service $(SERVICE) exists...)

# SERVICE="<name_of_service>" must be passed as ARG for target or else fail
ifndef SERVICE
	$(error [!] SERVICE env not defined...FAIL)
endif

ifeq ($(wildcard $(SERVICE)/.),)
	$(error [!] '$(SERVICE)' folder doesn't exist)
endif

_clone_service_to_build:
ifeq ($(wildcard build/.),)
	$(info [+] Cloning ${SERVICE} directory structure to build/${SERVICE})
	mkdir build
	rsync -a -f "+ */" -f "- *" ${SERVICE}/ build/${SERVICE}/
	$(info [+] Cloning source files from ${SERVICE} to build/${SERVICE}/)
	@find ${SERVICE} -type f \
			-not -name "*.pyc" \
			-not -name "*__pycache__" \
			-not -name "requirements.txt" \
			-not -name "event.json" \
			-not -name "build" | cut -d '/' -f2- > .results.txt
	@while read line; do \
		ln -f ${SERVICE}/$$line build/${SERVICE}/$$line; \
	done < .results.txt
	rm -f .results.txt
else
	$(info [-] '$(SERVICE)' already has a development build - Ignoring cloning task...)
endif

_check_dev_definition: _check_service_definition
	$(info [*] Checking whether service $(SERVICE) development build exists...)

ifeq ($(wildcard build/$(SERVICE)/.),)
	$(warning [FIX] run 'make build SERVICE=$(SERVICE)' to create one")
	$(error [!] '$(SERVICE)' doesn't have development build)
endif

_install_deps:
	$(info [+] Installing '$(SERVICE)' dependencies...")	
	@pip install pipenv
	@pipenv lock -r > requirements.txt
	@pipenv run pip install \
		--isolated \
		--disable-pip-version-check \
		-Ur requirements.txt -t build/

# Package application and devs together in expected zip from build
_package: _clone_service_to_build _check_service_definition _install_deps
	@$(MAKE) _zip SERVICE="${SERVICE}"

# As its name states: Zip everything up from build
_zip: _check_dev_definition 
	$(info [+] Creating '$(SERVICE)' ZIP...")
	@cd build/${SERVICE} && zip -rq -9 "$(BASE)/$(SERVICE).zip" * \
	--exclude "wheel/*" "setuptools/*" "pkg_resources/*" "pip/*" \
			  "easy_install.py" "__pycache__/*" "*.dist-info/*" "./**/__pycache__/*"
	$(info [*] Build complete: $(BASE)/$(SERVICE).zip)

define HELP_MESSAGE
	Environment variables to be aware of or to hardcode depending on your use case:

	SERVICE
		Default: {{ cookiecutter.project_module_slug }}
		Info: Environment variable to declare where source code for lambda is

	DOCKER
		Default: 1
		Info: Environment variable to declare whether Docker should be used to build. (Leaving Docker builds enabled is recommended.)

	STACK
		Default: {{ cookiecutter.project_slug }}
		Info: Environment variable to declare the name of the CloudFormation stack to deploy.

	REGION
		Default: us-east-1
		Info: Environment variable to declare which AWS region should be deployed to.

	BUCKET
		Default: not_defined
		Info: Environment variable to declare which AWS S3 bucket the Lambda package should be uploaded to and deployed from.

	Common usage:

	...::: Installs all required packages as defined in the pipfile :::...
	$ make install

	...::: Spawn a virtual environment shell :::...
	$ make shell

	...::: Cleans up the environment - Deletes Virtualenv, ZIP builds and Dev env :::...
	$ make clean

	...::: Creates local dev environment for Python hot-reloading w/ packages:::...
	$ make build

	...::: Bundles app and dependencies into a ZIP file using Docker:::...
	$ make package

	...::: Bundles app and dependencies into a ZIP file _without_ using Docker :::...
	$ make package DOCKER=0

	...::: Uploads package to your S3 bucket
        $ make upload BUCKET=<bucketname>

        ...::: Deploys an uploaded package to Lambda
        $ make deploy

	...::: Deploys an uploaded package to Lambda in us-west-2
	$ make deploy REGION=us-west-2

	...::: Run SAM Local API Gateway :::...
	$ make run

	...::: Run Pytest under tests/ with pipenv :::...
	$ make test

	Advanced usage:

	...::: Run SAM Local API Gateway within a Docker Network :::...
	$ make run NETWORK="sam-network"
endef
