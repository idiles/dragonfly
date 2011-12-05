create database dragonfly default character set utf8 collate utf8_general_ci;
grant all on dragonfly.* to 'dragonfly'@'localhost' identified by 'dragonfly';
flush privileges;

