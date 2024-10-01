export APP_DB_URL="postgresql://whohacks:S3cret@localhost:5432/whohacks"
export OAUTH_OPENID="http://sso.hsp.sh/auth/realms/hsp/.well-known/openid-configuration"
export OAUTH_CLIENT_ID="fake-development-client-id"
env | grep APP_ > .env
env | grep OUATH_ > .env