#!/usr/bin/env bash
set -Eeuo pipefail

EMAIL="${EMAIL:-max@bitnode.one}"
GIT_NAME="${GIT_NAME:-Max Peter}"
KEY_PATH="${KEY_PATH:-$HOME/.ssh/id_ed25519_github}"
KEY_TITLE="${KEY_TITLE:-$(hostname)-github-ssh}"
SSH_CONFIG="$HOME/.ssh/config"
AGENT_ENV="$HOME/.ssh/agent.env"
BASHRC="$HOME/.bashrc"

log() { printf '\n==> %s\n' "$*"; }
have() { command -v "$1" >/dev/null 2>&1; }

mkdir -p "$HOME/.ssh"
chmod 700 "$HOME/.ssh"

log "Generate SSH key if missing"
if [ ! -f "$KEY_PATH" ]; then
  ssh-keygen -t ed25519 -C "$EMAIL" -f "$KEY_PATH" -N ""
else
  echo "SSH key already exists: $KEY_PATH"
fi
chmod 600 "$KEY_PATH"
chmod 644 "$KEY_PATH.pub"

log "Start or reuse ssh-agent"
if [ -f "$AGENT_ENV" ]; then
  . "$AGENT_ENV" >/dev/null 2>&1 || true
fi

if ! ssh-add -l >/dev/null 2>&1; then
  eval "$(ssh-agent -s)" >/dev/null
  cat > "$AGENT_ENV" <<EOV
export SSH_AUTH_SOCK="$SSH_AUTH_SOCK"
export SSH_AGENT_PID="$SSH_AGENT_PID"
EOV
  chmod 600 "$AGENT_ENV"
fi

log "Add key to ssh-agent if needed"
if ! ssh-add -l 2>/dev/null | grep -Fq "$KEY_PATH"; then
  ssh-add "$KEY_PATH"
else
  echo "Key already loaded in ssh-agent"
fi

log "Ensure ~/.bashrc reloads ssh-agent env"
if ! grep -q 'BEGIN git-ssh-agent' "$BASHRC" 2>/dev/null; then
  cat >> "$BASHRC" <<'EOBASH'

# BEGIN git-ssh-agent
if [ -f "$HOME/.ssh/agent.env" ]; then
  . "$HOME/.ssh/agent.env" >/dev/null 2>&1 || true
fi
# END git-ssh-agent
EOBASH
else
  echo "~/.bashrc loader already present"
fi

log "Write ~/.ssh/config block for GitHub"
touch "$SSH_CONFIG"
chmod 600 "$SSH_CONFIG"
if ! grep -q 'BEGIN github.com bitnode-one' "$SSH_CONFIG" 2>/dev/null; then
  cat >> "$SSH_CONFIG" <<EOCFG

# BEGIN github.com bitnode-one
Host github.com
  HostName github.com
  User git
  IdentityFile $KEY_PATH
  IdentitiesOnly yes
  AddKeysToAgent yes
# END github.com bitnode-one
EOCFG
else
  echo "SSH config block already present"
fi

log "Set default global Git identity"
git config --global user.name "$GIT_NAME"
git config --global user.email "$EMAIL"

log "Set useful global git aliases"
git config --global alias.st status
git config --global alias.br branch
git config --global alias.co checkout
git config --global alias.sw switch
git config --global alias.ci commit
git config --global alias.a "add -A"
git config --global alias.ds "diff --staged"
git config --global alias.lg "log --graph --decorate --oneline --all"
git config --global alias.last "log -1 HEAD"
git config --global alias.unstage "reset HEAD --"
git config --global alias.amend "commit --amend --no-edit"

log "Try automatic GitHub SSH key upload via gh"
if have gh && gh auth status >/dev/null 2>&1; then
  pubkey="$(cat "$KEY_PATH.pub")"
  if gh ssh-key list 2>/dev/null | grep -Fq "$pubkey"; then
    echo "Public key already present in GitHub account"
  else
    gh ssh-key add "$KEY_PATH.pub" --title "$KEY_TITLE" || true
  fi
else
  echo "gh not available or not authenticated."
  echo "Add this public key manually in GitHub Settings -> SSH and GPG keys:"
  echo
  cat "$KEY_PATH.pub"
  echo
fi

log "Test SSH connection to GitHub"
ssh -T git@github.com || true

cat <<EOM

Done.

Public key:
  $KEY_PATH.pub

To use SSH for your repo:
  git remote set-url origin git@github.com:bitnode-one/bitnode.one.git

Useful commands:
  git st
  git a
  git ci -m "message"
  git lg
EOM
