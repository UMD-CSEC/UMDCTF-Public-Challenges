# app.rb
require 'sinatra'
require 'erb'
require 'mysql2'
require 'logger'
require 'json'
require 'digest'

set :bind, '0.0.0.0'
set :show_exceptions, false

def load_config
        file = File.read('db-config.json')
        creds = JSON.parse(file)
end

get '/' do
	erb :index
end

get '/login' do
	config = load_config

	username = params[:username]
	password = params[:password]

	username = username.gsub(/'/,"\\\\'")	
	username = username.gsub(/"/,"\\\\\"")	
	password = password.gsub(/'/,"\\\\'")
	password = password.gsub(/"/,"\\\\\"")
	username = username.gsub(/or/,"")
	password = password.gsub(/or/,"")
	username = username.gsub(/OR/,"")
	password = password.gsub(/OR/,"")
	
	conn = Mysql2::Client.new(:host => config['host'], :username => config['username'], :password => config['password'], :database => config['database'])
	res = conn.query("select * from users where username='" + username + "' and password='" + password + "';")
	# Hope seeing this helps you crack the challenge ;)
	if res.size > 0
		res.each do |row|
			@user=row["username"].to_s
			@password=row["password"].to_s
		end
		erb :login
	else
		erb :index
	end
end


get '/about' do
	erb :about
end
