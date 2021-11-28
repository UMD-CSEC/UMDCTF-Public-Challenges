# app.rb
require 'sinatra'
require 'erb'
require 'mysql2'
require 'logger'
require 'json'
require 'digest'

set :bind, '0.0.0.0'
set :show_exceptions, false

get '/' do
	erb :index
end

get '/login' do
	erb :login
end


get '/about' do
	erb :about
end
