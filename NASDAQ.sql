CREATE TABLE IF NOT EXISTS `Articles` (
  `article_id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `author_id` int,
  `title` varchar(255),
  `article_content` varchar(255),
  `url` varchar(255),
  `published_date` datetime
);

CREATE TABLE IF NOT EXISTS `Authors` (
  `author_id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `author_name` varchar(255)
);

CREATE TABLE IF NOT EXISTS `Tags` (
  `tag_id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `tag_name` varchar(255)
);

CREATE TABLE IF NOT EXISTS `Article_Tags` (
  `article_tag_id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `article_id` int,
  `tag_id` int
);

CREATE TABLE IF NOT EXISTS `Stocks` (
  `stock_id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `stock_tick` varchar(255)
);

CREATE TABLE IF NOT EXISTS `Stock_Articles` (
  `stock_article_id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `stock_id` int,
  `article_id` int
);
