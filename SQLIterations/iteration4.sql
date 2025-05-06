CREATE TABLE historical_trades (
  id int NOT NULL AUTO_INCREMENT,
  symbol varchar(10) NOT NULL,
  timestamp datetime NOT NULL,
  open decimal(10,4) NOT NULL,
  high decimal(10,4) NOT NULL,
  low decimal(10,4) NOT NULL,
  close decimal(10,4) NOT NULL,
  volume bigint NOT NULL,
  trade_count int DEFAULT NULL,
  vwap decimal(10,4) DEFAULT NULL,
  PRIMARY KEY (id),
  KEY idx_symbol_timestamp (symbol,timestamp)
) 

CREATE TABLE politician_confidence (
  politician varchar(255) NOT NULL,
  confidence_score float DEFAULT NULL,
  PRIMARY KEY (politician)
) 

 CREATE TABLE politician_trades (
  id int NOT NULL AUTO_INCREMENT,
  politician varchar(255) DEFAULT NULL,
  traded_issuer varchar(255) DEFAULT NULL,
  ticker varchar(100) DEFAULT NULL,
  published_date varchar(100) DEFAULT NULL,
  trade_date varchar(100) DEFAULT NULL,
  gap varchar(50) DEFAULT NULL,
  trade_type varchar(50) DEFAULT NULL,
  page int DEFAULT NULL,
  party varchar(50) DEFAULT NULL,
  chamber varchar(50) DEFAULT NULL,
  state varchar(50) DEFAULT NULL,
  min_purchase_price decimal(10,2) DEFAULT NULL,
  max_purchase_price decimal(10,2) DEFAULT NULL,
  min_roi decimal(10,2) DEFAULT NULL,
  max_roi decimal(10,2) DEFAULT NULL,
  avg_roi decimal(10,2) DEFAULT NULL,
  image varchar(255) DEFAULT NULL,
  confidence_score float DEFAULT NULL,
  PRIMARY KEY (id)
) 

CREATE TABLE users (
    id INT NOT NULL AUTO_INCREMENT,
    username VARCHAR(255) UNIQUE,
    email VARCHAR(255) UNIQUE,
    password VARCHAR(255),
    PRIMARY KEY (id)
)