# {{ cookiecutter.project_name }}

{{ cookiecutter.project_short_description }}

## Super Quick Start!
If you have local AWS credentials available, S3 and CloudFormation permissions, and have already installed the [required software](#requirements), you can deploy a function **right now**:

```bash
aws mb s3://my-bucket-rename-me
make install && make package && make upload BUCKET=my-bucket-rename-me && make deploy
```

Once the CloudFormation run completes you will find a Lambda function named {{ cookiecutter.lambda_function_name }} in the us-east-1 region (pass the `REGION` env variable to `make deploy` to change this, e.g. `make deploy REGION=us-west-2`) using an execution role named {{ cookiecutter.lambda_function_name }}.LambdaRole.

## Requirements

* AWS CLI already configured with at least PowerUser permission
* [Python 3 installed](https://www.python.org/downloads/)
* [Pipenv installed](https://github.com/pypa/pipenv)
    - `pip install pipenv`
* [Docker installed](https://www.docker.com/community-edition)
* [SAM Local installed](https://github.com/awslabs/aws-sam-local) 

Provided that you have requirements above installed, proceed by installing the application dependencies and development dependencies:

```bash
make install
```

This is equivalent to `pipenv install && pipenv install -d` and will create a virtualenv which you can enter with `make shell` (or `pipenv shell`).

## Testing

`Pytest` is used to discover tests created under `tests` folder - Here's how you can run tests our initial unit tests:

```bash
make test
```

This is equivalent to `pipenv run python -m pytest tests/ -v`

**Tip**: Commands passed to `pipenv run` will be executed in the Virtual environment created for our project.

## Packaging

AWS Lambda Python runtime requires a flat folder with all dependencies including the application. To facilitate this process, the pre-made SAM template expects this structure to be under `build/`:

```yaml
...
    {{ cookiecutter.lambda_function_name }}:
        Type: AWS::Serverless::Function
        Properties:
            CodeUri: build/
            ...
```

`make build` will install all of the required dependencies to `build/`, and hard-link the contents of your module directory so that you don't need to re-build when changing existing files.

`make package` does the same thing as `make build`, but it does so inside a [LambCI Lambda Docker container](https://hub.docker.com/r/lambci/lambda/) by default (disable this by setting `DOCKER=0`) to ensure that any C-extensions or other platform-specific doodads will work correctly in the Lambda execution environment. It creates a Zip file of the resulting build that is appropriate for uploading and deploying to Lambda.

### Local development

Given that you followed Packaging instructions then run one of the following options to invoke your function locally:

**Invoking function locally without API Gateway**

```bash
echo '{"lambda": "payload"}' | sam local invoke {{ cookiecutter.lambda_function_name }}
```

**Invoking function locally through local API Gateway**

```bash
sam local start-api
```

If the previous command run successfully you should now be able to hit the following local endpoint to invoke your function `http://localhost:3000/first/REPLACE-ME-WITH-ANYTHING`.

## Deployment

*The following instructions assume you have local AWS credentials available and permission to perform the relevant S3 and CloudFormation actions.*

First and foremost, we need a S3 bucket where we can upload our Lambda functions packaged as ZIP before we deploy anything - If you don't have a S3 bucket to store code artifacts then this is a good time to create one:

```bash
aws s3 mb s3://BUCKET_NAME
```

Provided you have a S3 bucket created, run the following command to package our Lambda function to S3:
```bash
make upload BUCKET=<bucket_name>
```

This is equivalent to:
```bash
aws cloudformation package \
    --template-file template.yaml \
    --output-template-file packaged.yaml \
    --s3-bucket <bucket_name>
```

Next, the following command will create a Cloudformation Stack and deploy your SAM resources.

```bash
make deploy
```

This is equivalent to:
```bash
aws cloudformation deploy \
    --template-file packaged.yaml \
    --stack-name {{ cookiecutter.project_slug }} \
    --capabilities CAPABILITY_NAMED_IAM
    --region us-east-1
```

> **See [Serverless Application Model (SAM) HOWTO Guide](https://github.com/awslabs/serverless-application-model/blob/master/HOWTO.md) for more details in how to get started.**

{% if cookiecutter.include_apigw == "y" %}
After deployment is complete you can run the following command to retrieve the API Gateway Endpoint URL:

```bash
aws cloudformation describe-stacks \
    --stack-name {{ cookiecutter.project_slug }} \
    --query 'Stacks[].Outputs'
``` 
{% endif %}

