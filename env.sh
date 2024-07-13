export APP_DB_URL="postgresql://whohacks:S3cret@localhost:5432/whohacks"
export OAUTH_OPENID="http://sso.hsp.sh/auth/realms/hsp/.well-known/openid-configuration"
env | grep APP_ > .env
env | grep OUATH_ > .env