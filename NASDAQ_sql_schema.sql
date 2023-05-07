CREATE TABLE IF NOT EXISTS `Articles` (
  `article_id` INTEGER PRIMARY KEY AUTO_INCREMENT,
  `author_id` int,
  `title` varchar(255),
  `article_content` LONGTEXT,
  `url` varchar(255),
  `published_date` datetime,
  CONSTRAINT `FK_Articles_Authors` FOREIGN KEY (`author_id`)
  REFERENCES `Authors` (`author_id`)
  ON DELETE CASCADE
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
  `tag_id` int,
  CONSTRAINT `FK_Article_Tags_Articles` FOREIGN KEY (`article_id`)
    REFERENCES `Articles` (`article_id`)
    ON DELETE CASCADE,
  CONSTRAINT `FK_Article_Tags_Tags` FOREIGN KEY (`tag_id`)
    REFERENCES `Tags` (`tag_id`)
    ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS `Stocks` (
  `stock_id` INTEGER PRIMARY KEY AUTO_INCREMENT,
  `stock_tick` varchar(255),
  `name` varchar(255),
  `currency` varchar(255),
  `country` varchar(255),
  `sector` varchar(255),
  `industry` varchar(255)
);

CREATE TABLE IF NOT EXISTS `Stocks_Prices` (
  `stock_price_id` INTEGER PRIMARY KEY AUTO_INCREMENT,
  `stock_id` int,
  `date` datetime,
  `open` int,
  `high` int,
  `low` int,
  `close` int,
  `volume` int,
  CONSTRAINT `FK_Stocks_Prices_Stocks` FOREIGN KEY (`stock_id`)
    REFERENCES `Stocks` (`stock_id`)
    ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS `Stock_Articles` (
  `stock_article_id` INTEGER PRIMARY KEY AUTO_INCREMENT,
  `stock_id` int,
  `article_id` int,
  CONSTRAINT `FK_Stock_Articles_Stocks` FOREIGN KEY (`stock_id`)
    REFERENCES `Stocks` (`stock_id`)
    ON DELETE CASCADE,
  CONSTRAINT `FK_Stock_Articles_Articles` FOREIGN KEY (`article_id`)
    REFERENCES `Articles` (`article_id`)
    ON DELETE CASCADE
);


