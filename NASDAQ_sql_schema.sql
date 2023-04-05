CREATE TABLE IF NOT EXISTS `Articles` (
  `article_id` INTEGER PRIMARY KEY AUTO_INCREMENT,
  `author_id` int,
  `title` varchar(255),
  `article_content` LONGTEXT,
  `url` varchar(255),
  `published_date` datetime
);

CREATE TABLE IF NOT EXISTS `Authors` (
  `author_id` INTEGER PRIMARY KEY AUTO_INCREMENT,
  `author_name` varchar(255)
);

CREATE TABLE IF NOT EXISTS `Tags` (
  `tag_id` INTEGER PRIMARY KEY AUTO_INCREMENT,
  `tag_name` varchar(255)
);

CREATE TABLE IF NOT EXISTS `Article_Tags` (
  `article_tag_id` INTEGER PRIMARY KEY AUTO_INCREMENT,
  `article_id` int,
  `tag_id` int
);

CREATE TABLE IF NOT EXISTS `Stocks` (
  `stock_id` INTEGER PRIMARY KEY AUTO_INCREMENT,
  `stock_tick` varchar(255)
);

CREATE TABLE IF NOT EXISTS `Stock_Articles` (
  `stock_article_id` INTEGER PRIMARY KEY AUTO_INCREMENT,
  `stock_id` int,
  `article_id` int
);
