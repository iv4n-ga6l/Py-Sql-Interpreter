## Sql interpreter

Simple sql interpreter built in Python with local sqlite database. Work both in CLI & Web mode.
It supports :
- Database creation
- Tables (CRUD)
- Tables export to csv files and tables restoration using csv files 
- Database backup and restoration

### Example queries
```sql
** CREATE DATABASE Shop


**Example create

CREATE TABLE Category (
    Id INT PRIMARY KEY,
    libelle VARCHAR(255)
);


CREATE TABLE Items (
    ItemID INT PRIMARY KEY,
    ItemName VARCHAR(255),
    Price DECIMAL(10, 2),
    StockQuantity INT,
    CategoryId INT,
    FOREIGN KEY (CategoryId) REFERENCES Category(Id)
);

CREATE TABLE Recruiters (
    RecruiterName VARCHAR(255) PRIMARY KEY,
    Cabinet VARCHAR(255),
    LinkedIn VARCHAR(255),
    Mail VARCHAR(255)
);



**Example insert

INSERT INTO Category (Id, libelle)
VALUES (1, 'Electronique');

INSERT INTO Category (Id, libelle)
VALUES (2, 'Accesory');


INSERT INTO Items (ItemID, ItemName, Price, StockQuantity, CategoryId)
VALUES (1, 'Phone', 299, 150, 1);

INSERT INTO Items (ItemID, ItemName, Price, StockQuantity, CategoryId)
VALUES (2, 'Watch', 100, 40, 1);


INSERT INTO Items (ItemID, ItemName, Price, StockQuantity, CategoryId)
VALUES (3, 'Bag', 99, 60, 2);


** SELECT JOIN

SELECT c.libelle FROM Items i JOIN Category c ON i.CategoryId = c.Id WHERE i.ItemID = 1;

SELECT i.ItemName, c.libelle FROM Items i JOIN Category c ON i.CategoryId = c.Id WHERE i.ItemID = 1;

SELECT c.libelle, COUNT(i.ItemID) AS NumberOfItems FROM Category c LEFT JOIN Items i ON c.Id = i.CategoryId GROUP BY c.libelle;


**Example update
UPDATE Items SET Price = 24.99 WHERE ItemID = 1;

**Example delete
DELETE FROM Items WHERE ItemID=1;

**Example drop
DROP TABLE Items;
```

### Run
- Web
```sh
python app.py
```

- CLI
```sh
python app.py --mode cli
```