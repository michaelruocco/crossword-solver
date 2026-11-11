# AWS and GitHub Bootstrap

Complete this setup before the first local deployment or deployment pipeline run. Install
Terraform 1.10 or newer and AWS CLI v2, and configure AWS credentials for an administrator/bootstrap
identity in the target account. Never run bootstrap with the application deployment role.
Run all commands from the repository root.

The shell script creates the shared state bucket. The separate Terraform configuration manages
GitHub OIDC authentication and deployment-role permissions; it does not create application resources.

## 1. Create the Shared State Bucket

Terraform needs an existing S3 bucket before it can initialize the application's remote backend.
Create this bucket once per account/project. It is shared by environments, with a separate
state key for each environment.

Choose a globally unique bucket name and set the target region:

```sh
export TF_STATE_BUCKET="<globally-unique-bucket-name>"
export AWS_REGION="eu-west-2"

./infrastructure/bootstrap/setup-state-bucket.sh "$TF_STATE_BUCKET" "$AWS_REGION"
```

The [script](setup-state-bucket.sh) enables versioning, default encryption, bucket-owner enforcement,
and S3 public-access blocking. The bucket is created outside the application's Terraform
configuration, so destroying an application environment does not delete its state bucket.
Do not delete the bucket while its state is still needed.

Subsequent deployments and additional environments in the same account reuse the bucket;
do not rerun the creation script. Set the same `TF_STATE_BUCKET` value when returning in a new
shell. Each environment uses `crossword-solver/<environment>/terraform.tfstate` in this bucket.
For existing infrastructure, migrate local application state to its matching S3 key before
the first pipeline run; do not initialize empty state to manage existing resources.

## 2. Create and Protect the GitHub Environment

Under **Settings > Environments**, create the target environment (for example, `dev`).
Use lowercase letters, digits, and hyphens, starting with a letter. Configure deployment
protection rules to allow only trusted branches and tags and add required reviewers where needed.
The workflow's environment-based OIDC subject relies on these rules to restrict which code
can assume the role.

## 3. Configure AWS Authentication

The Terraform configuration registers GitHub's OIDC provider at
`https://token.actions.githubusercontent.com` with audience `sts.amazonaws.com` when requested,
and creates an IAM deployment role with a project-scoped policy. Its trust policy allows only
the configured repository and GitHub environment, for example
`repo:michaelruocco/crossword-solver:environment:dev`. No AWS access keys are stored in GitHub.

If the role already exists, follow **Adopt an Existing Role** below before the first plan/apply.
For a new role and an account without GitHub's OIDC provider:

```sh
terraform -chdir=infrastructure/bootstrap init
terraform -chdir=infrastructure/bootstrap plan \
  -var="aws_region=$AWS_REGION" \
  -var="state_bucket=$TF_STATE_BUCKET" \
  -var='create_oidc_provider=true' \
  -out=bootstrap.tfplan
terraform -chdir=infrastructure/bootstrap apply bootstrap.tfplan
terraform -chdir=infrastructure/bootstrap output -raw aws_role_arn
```

`aws_region` defaults to `eu-west-2`; `github_repository` defaults to
`michaelruocco/crossword-solver`. Save your chosen inputs in an untracked Terraform variable file
for subsequent plans, or pass exactly the same flags each time.

If the GitHub OIDC provider already exists in this account, omit `create_oidc_provider=true`.
Only one bootstrap state should own the shared provider. Do not change that flag to false
after creating it: Terraform would plan to delete the provider.

## 4. Configure GitHub Actions Variables

Add these GitHub Actions variables at repository level, or override them in each environment:

| Variable          | Value                                               |
| ----------------- | --------------------------------------------------- |
| `AWS_ROLE_ARN`    | Deployment-role ARN from the Terraform output above |
| `TF_STATE_BUCKET` | Name of the existing shared state bucket            |
| `AWS_REGION`      | Deployment region; defaults to `eu-west-2`          |
| `TF_STATE_REGION` | State bucket region; defaults to `AWS_REGION`       |

Use the same bucket and target region chosen above. The deployment workflow does not
create the state bucket or OIDC resources. After completing bootstrap, continue with
[layer publication and deployment](../../README.md#2-publish-the-opencv-layer).

## Reusing an Existing OIDC Provider

If the GitHub OIDC provider already exists in your AWS account (created for another project),
simply omit `create_oidc_provider=true` when running terraform. The role's trust policy will
reference the existing account-level provider at `https://token.actions.githubusercontent.com`.

## State and Environments

Bootstrap uses local state by default, independently of the application's S3 backend. Protect
and back up this state; do not commit it. For shared administration, configure a separate remote
backend/key and migrate the bootstrap state using Terraform's normal state migration procedure.
Never reuse the application's state key or run application destroy commands in this directory.

A single role created by this bootstrap can deploy to all environments (dev, prod, staging, etc.)
within the same AWS account. The role's trust policy allows GitHub Actions from any environment,
and resource-level permissions are isolated via the `crossword-solver-*` naming prefix, which
ensures the role can only access resources for your application across all environments.

## Permissions

The policy includes role tagging, limits IAM role management to Lambda roles, and restricts
`PassRole` to Lambda. State access is granted for all environments via wildcard patterns.
Application S3 buckets, Lambda functions/layers, DynamoDB tables, and SQS queues use the
prefix `crossword-solver-*` to match any environment across the selected region/account.

Lambda role management requires `iam:TagRole` and `iam:UntagRole` on roles named
`crossword-solver-*-lambda`: the application AWS provider applies `Application` and
`Environment` default tags. The policy also grants `s3:ListBucket` on the state bucket,
`s3:GetObject` and `s3:PutObject` on all environment state objects, and `s3:GetObject`,
`s3:PutObject`, and `s3:DeleteObject` on their `.tflock` objects.

This is a project-scoped deployment policy, not strict least privilege: service wildcards
allow management of the named resources, including their data. HTTP API IDs, Lambda event-source
mapping IDs, and CloudFront IDs are generated, so their permissions cover other resources of
those types in the selected region/account (CloudFront operations use `*`). Creating a tagged
role requires `iam:TagRole` as well as `iam:CreateRole`.

The deploy role can write inline policies to application Lambda roles and pass them to Lambda;
this is privileged access, not an IAM privilege-escalation boundary. Restrict GitHub environment
access accordingly. Add organizational permissions boundaries/SCPs when stronger isolation is
required. Review this policy whenever Terraform adds a service or changes naming conventions.
The policy intentionally cannot modify the deployment role or OIDC provider itself.

Application deployments must use Terraform's default workspace: the state object path is
environment-specific already. Bucket listing also allows the backend's `env:/` workspace
discovery prefix, but does not grant read/write access to non-default workspace state objects.

Review every bootstrap plan before applying. No AWS resources are changed just by adding this
configuration to the repository.

## Local Validation

```sh
terraform -chdir=infrastructure/bootstrap fmt -check
terraform -chdir=infrastructure/bootstrap validate
terraform -chdir=infrastructure/bootstrap test
```

The tests use dummy credentials and override AWS identity data. They only plan and evaluate
the policy locally; they do not call AWS or create resources. A real bootstrap plan/apply and
deployment are still needed to verify permissions against your account's policies and SCPs.
