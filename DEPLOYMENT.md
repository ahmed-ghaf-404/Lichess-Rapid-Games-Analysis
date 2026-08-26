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

## Create the deployment SSH key

Use a **new, dedicated key** for GitHub Actions. Do not reuse your personal SSH
key. The memory rule is simple: **the public key goes on the VPS; the private
key goes into the `PROD_SSH_KEY` GitHub Environment secret. Never commit either
key.**

On your Mac, run this once:

```bash
ssh-keygen -t ed25519 -a 100 -C "ccc-github-actions" -f ~/.ssh/ccc_github_actions
```

The deployment workflow does not provide a passphrase, so press Enter for an
empty passphrase when prompted. This is acceptable only because this key is
dedicated to deployment and stored as an encrypted GitHub secret.

This creates two files:

| File | Keep it where? | Purpose |
| --- | --- | --- |
| `~/.ssh/ccc_github_actions` | Your Mac and `PROD_SSH_KEY` only | Private key; never share or commit it |
| `~/.ssh/ccc_github_actions.pub` | VPS `authorized_keys` only | Public key; safe to install on the server |

### Install the public key on the VPS

Connect to the Hostinger VPS as its initial administrator, create a dedicated
deployment user, and allow it to use Docker:

```bash
adduser cccdeploy
usermod -aG docker cccdeploy
install -d -m 700 -o cccdeploy -g cccdeploy /home/cccdeploy/.ssh
```

On your Mac, copy the public key:

```bash
pbcopy < ~/.ssh/ccc_github_actions.pub
```

Back on the VPS, open the allowed-keys file, paste the copied one-line public
key, save, then set its permissions:

```bash
nano /home/cccdeploy/.ssh/authorized_keys
chown cccdeploy:cccdeploy /home/cccdeploy/.ssh/authorized_keys
chmod 600 /home/cccdeploy/.ssh/authorized_keys
```

Test the key from your Mac before adding it to GitHub:

```bash
ssh -i ~/.ssh/ccc_github_actions cccdeploy@deploy.yourdomain.com
```

It should log in without asking for the VPS password. Replace
`deploy.yourdomain.com` with a Hostinger DNS hostname that points to your VPS;
this keeps the raw IP address out of GitHub.

Finally, copy the **private** key and paste it as the multi-line
`PROD_SSH_KEY` Environment secret in GitHub:

```bash
pbcopy < ~/.ssh/ccc_github_actions
```

Clear your clipboard afterwards if you prefer:

```bash
pbcopy < /dev/null
```

The `docker` group has broad control of the server, so treat this deployment key
as highly sensitive. Store a backup in a password manager, never paste it into
chat or source control, and rotate it by creating a new dedicated key, testing
it, replacing `PROD_SSH_KEY`, then removing the old public-key line from the
VPS.

## Release flow

1. Merge reviewed work into `main`.
2. Fast-forward `prod` to the release commit.
3. Push `prod` when ready to deploy.
4. Confirm both **CI** and **Deploy production** pass in GitHub Actions.

The workflow never commits secrets. Example environment files document every
required key, while `.dockerignore` prevents real environment files from being
copied into container images.
