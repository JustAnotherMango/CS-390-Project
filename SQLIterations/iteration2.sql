CREATE TABLE Users
(
  UserID INT NOT NULL,
  Username VARCHAR(50) NOT NULL,
  Email VARCHAR(50) NOT NULL,
  PasswordHash VARCHAR(250) NOT NULL,
  Role VARCHAR(50) NOT NULL,
  PRIMARY KEY (UserID)
);

CREATE TABLE Politicians
(
  PoliticianID VARCHAR(50) NOT NULL,
  Name VARCHAR(50) NOT NULL,
  Party VARCHAR(20) NOT NULL,
  Position VARCHAR(50) NOT NULL,
  PRIMARY KEY (PoliticianID)
);

CREATE TABLE StockMarketData
(
  StockSymbol VARCHAR(10) NOT NULL,
  Date DATE NOT NULL,
  Open TIME NOT NULL,
  Close TIME NOT NULL,
  High FLOAT NOT NULL,
  Low FLOAT NOT NULL,
  Volume FLOAT NOT NULL,
  PRIMARY KEY (StockSymbol, Date)
);

CREATE TABLE API_Requests
(
  RequestID INT NOT NULL,
  RequestTime TIME NOT NULL,
  Username VARCHAR(50) NOT NULL,
  Status VARCHAR(50) NOT NULL,
  UserID INT NOT NULL,
  PRIMARY KEY (RequestID),
  FOREIGN KEY (UserID) REFERENCES Users(UserID)
);

CREATE TABLE InterfaceTrades
(
  TradedIssuer INT NOT NULL,
  PublishedDate DATE NOT NULL,
  TradeDate DATE NOT NULL,
  GapUnit VARCHAR(50) NOT NULL,
  TradeType VARCHAR(50) NOT NULL,
  Shares FLOAT NOT NULL,
  Page INT NOT NULL
);

CREATE TABLE Trades
(
  TradeID INT NOT NULL,
  TradeType VARCHAR(50) NOT NULL,
  TradeDate DATE NOT NULL,
  Shares FLOAT NOT NULL,
  PricePerShare FLOAT NOT NULL,
  TotalValue FLOAT NOT NULL,
  PublishedDate DATE NOT NULL,
  GapUnit VARCHAR(50) NOT NULL,
  Gap VARCHAR(50) NOT NULL,
  Page INT NOT NULL,
  PoliticianID VARCHAR(50) NOT NULL,
  StockSymbol VARCHAR(10) NOT NULL,
  Date DATE NOT NULL,
  PRIMARY KEY (TradeID),
  FOREIGN KEY (PoliticianID) REFERENCES Politicians(PoliticianID),
  FOREIGN KEY (StockSymbol, Date) REFERENCES StockMarketData(StockSymbol, Date)
);

CREATE TABLE Confidence
(
  ConfidenceID INT NOT NULL,
  StockSymbol VARCHAR(10) NOT NULL,
  ConfidenceScore FLOAT NOT NULL,
  TimeStamp TIME NOT NULL,
  PoliticianID VARCHAR(50) NOT NULL,
  TradeID INT NOT NULL,
  PRIMARY KEY (ConfidenceID),
  FOREIGN KEY (PoliticianID) REFERENCES Politicians(PoliticianID),
  FOREIGN KEY (TradeID) REFERENCES Trades(TradeID)
);
