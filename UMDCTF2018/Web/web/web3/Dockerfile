FROM ruby
RUN apt-get update
RUN apt-get install -y default-libmysqlclient-dev ruby-mysql2
MAINTAINER michael@csec.umiacs.umd.edu


COPY src /usr/local/src
WORKDIR /usr/local/src
RUN gem install sinatra
RUN gem install mysql2
RUN gem install sinatra-contrib

EXPOSE 4567
CMD ["ruby","/usr/local/src/app.rb"]
