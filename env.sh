export APP_DB_DIALECT="postgresql"
export APP_DB_NAME="whohacks"
export APP_DB_USER="whohacks"
export APP_DB_PASSWORD="S3cret"
export APP_DB_HOST="localhost"
export APP_DB_PORT="5432"
export APP_OAUTH_OPENID="http://sso.hsp.sh/auth/realms/hsp/.well-known/openid-configuration"
env | grep APP_ > .env