# Production deployment

Production deploys are branch-gated. A push to `prod` runs the full CI
workflow. Only after that workflow succeeds does the deployment workflow
connect to the server and update the Docker Compose stack.

## One-time GitHub setup

Create a protected GitHub environment named `production`, then add these
environment secrets:

| Secret | Purpose |
| --- | --- |
| `PROD_HOST` | Server hostname or IP address |
| `PROD_USER` | SSH user allowed to run Docker Compose |
| `PROD_SSH_KEY` | Private SSH key for that user |
| `PROD_APP_PATH` | Absolute path to the existing server checkout |

Require reviewer approval on the `production` environment if you want a manual
gate after CI. The server checkout must already contain its real, untracked
`coach-ai/.env` and `game-scraper/.env` files and must have access to the
external `caddy_net` Docker network referenced by `docker-compose.yml`.

## Release flow

1. Merge reviewed work into `main`.
2. Fast-forward `prod` to the release commit.
3. Push `prod` when ready to deploy.
4. Confirm both **CI** and **Deploy production** pass in GitHub Actions.

The workflow never commits secrets. Example environment files document every
required key, while `.dockerignore` prevents real environment files from being
copied into container images.
