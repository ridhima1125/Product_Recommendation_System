CREATE DATABASE rec_db;
USE rec_db;

CREATE TABLE products (
    product_id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(200),
    category VARCHAR(50),
    brand VARCHAR(100),
    price DECIMAL(10,2),
    rating DECIMAL(3,1),
    description TEXT
);

CREATE TABLE users (
    user_id VARCHAR(10) PRIMARY KEY,
    user_name VARCHAR(100),
    city VARCHAR(100),
    age INT
);

CREATE TABLE ratings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(10),
    product_id VARCHAR(10),
    rating DECIMAL(3,1),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

USE rec_db;

-- 1. Top 10 most popular products
SELECT p.name, p.category,
       COUNT(r.id) AS total_ratings,
       ROUND(AVG(r.rating),2) AS avg_rating
FROM ratings r JOIN products p ON r.product_id=p.product_id
GROUP BY p.product_id, p.name, p.category
ORDER BY total_ratings DESC LIMIT 10;

-- 2. Category performance
SELECT p.category,
       COUNT(DISTINCT r.user_id) AS unique_users,
       ROUND(AVG(r.rating),2) AS avg_rating
FROM ratings r JOIN products p ON r.product_id=p.product_id
GROUP BY p.category ORDER BY avg_rating DESC;

-- 3. Most active users
SELECT u.user_name, u.city,
       COUNT(r.id) AS products_rated
FROM ratings r JOIN users u ON r.user_id=u.user_id
GROUP BY r.user_id, u.user_name, u.city
ORDER BY products_rated DESC LIMIT 10;

-- 4. Price range vs rating (CASE WHEN = SQL ka if-else!)
SELECT
    CASE WHEN p.price > 10000 THEN 'Premium'
         WHEN p.price > 2000  THEN 'Mid Range'
         ELSE 'Budget' END AS price_range,
    ROUND(AVG(r.rating),2) AS avg_rating,
    COUNT(r.id) AS total_ratings
FROM ratings r JOIN products p ON r.product_id=p.product_id
GROUP BY price_range;

-- 5. City wise users
SELECT city, COUNT(*) AS users
FROM users GROUP BY city ORDER BY users DESC;