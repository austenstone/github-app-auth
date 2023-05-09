require 'octokit'

require 'openssl'
require 'jwt'  # https://rubygems.org/gems/jwt

APP_ID = ENV['GITHUB_APP_ID']
PRIVATE_KEY_PATH = 'private-key.pem'
INSTALLATION_ID = ENV['GITHUB_INSTALLATION_ID']

# Private key contents
private_pem = File.read(PRIVATE_KEY_PATH)
private_key = OpenSSL::PKey::RSA.new(private_pem)

# Generate the JWT
payload = {
  # issued at time, 60 seconds in the past to allow for clock drift
  iat: Time.now.to_i - 60,
  # JWT expiration time (10 minute maximum)
  exp: Time.now.to_i + (10 * 60),
  # GitHub App's identifier
  iss: APP_ID
}

jwt = JWT.encode(payload, private_key, "RS256")
puts jwt

client = Octokit::Client.new(:bearer_token => jwt)

puts client.create_app_installation_access_token(INSTALLATION_ID)[:token]
