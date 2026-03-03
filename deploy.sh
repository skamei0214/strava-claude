#!/bin/bash
# Deploys the remote MCP server to the Hostinger VPS
set -e

VPS_IP="187.77.203.66"
VPS_USER="root"
REMOTE_DIR="/opt/strava-mcp-ringo"

echo "→ Copying files to VPS..."
ssh "$VPS_USER@$VPS_IP" "mkdir -p $REMOTE_DIR"
scp strava_mcp_server_http.js package.json .env "$VPS_USER@$VPS_IP:$REMOTE_DIR/"

echo "→ Installing dependencies on VPS..."
ssh "$VPS_USER@$VPS_IP" "cd $REMOTE_DIR && npm install --omit=dev"

echo "→ Restarting service..."
ssh "$VPS_USER@$VPS_IP" "systemctl restart strava-mcp-ringo"

echo "✓ Deploy complete"
