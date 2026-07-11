SELECT COUNT(*) FROM companies;

SELECT * FROM companies LIMIT 10;

SELECT sector, COUNT(*)
FROM sectors
GROUP BY sector;

SELECT *
FROM stock_prices
ORDER BY Date DESC
LIMIT 20;