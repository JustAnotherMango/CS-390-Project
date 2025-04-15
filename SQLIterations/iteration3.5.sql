CREATE TABLE politicians (
  id INT NOT NULL AUTO_INCREMENT,
  name VARCHAR(255) NOT NULL,
  party VARCHAR(50),
  chamber VARCHAR(50),
  state VARCHAR(50),
  image VARCHAR(255),
  PRIMARY KEY (id)
);

CREATE TABLE trade_metadata (
  id INT NOT NULL AUTO_INCREMENT,
  gap_unit VARCHAR(50),
  gap VARCHAR(50),
  trade_type VARCHAR(50),
  page INT,
  min_purchase_price DECIMAL(10,2),
  max_purchase_price DECIMAL(10,2),
  min_roi DECIMAL(10,2),
  max_roi DECIMAL(10,2),
  avg_roi DECIMAL(10,2),
  PRIMARY KEY (id)
);

CREATE TABLE politician_trades (
  id INT NOT NULL AUTO_INCREMENT,
  politician_id INT NOT NULL,
  traded_issuer VARCHAR(255),
  ticker VARCHAR(100),
  published_date VARCHAR(100),
  trade_date VARCHAR(100),
  metadata_id INT,
  PRIMARY KEY (id),
  FOREIGN KEY (politician_id) REFERENCES politicians(id),
  FOREIGN KEY (metadata_id) REFERENCES trade_metadata(id)
);

CREATE TABLE historical_trades (
  id INT NOT NULL AUTO_INCREMENT,
  symbol VARCHAR(10) NOT NULL,
  timestamp DATETIME NOT NULL,
  open DECIMAL(10,4) NOT NULL,
  high DECIMAL(10,4) NOT NULL,
  low DECIMAL(10,4) NOT NULL,
  close DECIMAL(10,4) NOT NULL,
  volume BIGINT NOT NULL,
  trade_count INT DEFAULT NULL,
  vwap DECIMAL(10,4) DEFAULT NULL,
  PRIMARY KEY (id),
  KEY idx_symbol_timestamp (symbol, timestamp)
);
