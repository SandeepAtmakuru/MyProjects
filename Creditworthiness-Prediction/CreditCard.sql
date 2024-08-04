use creditcard;
select * from creditcard;
-- 1.Group the customers based on their income type and find the average of their annual income.
SELECT 
    Type_Income,
    ROUND(AVG(Annual_income), 2) AS 'Average Annual income'
FROM
    creditcard
GROUP BY Type_Income;



-- 2.Find the female owners of cars and property.
SELECT 
    *
FROM
    creditcard
WHERE
    Gender = 0 AND Car_Owner = 1
        AND Propert_Owner = 1;



-- 3.Find the male customers who are staying with their families.
SELECT 
    *
FROM
    creditcard
WHERE
    Family_Members > 1 AND Gender = 1;

-- 4.Please list the top five people having the highest income.
SELECT 
    *
FROM
    creditcard
ORDER BY Annual_income DESC
LIMIT 5;

-- 5.How many married people are having bad credit?
#Here I changed it from 1 to 0 for better understanding 0 means Rejected and 1 means selected Accepted
SELECT 
    *
FROM
    creditcard
WHERE
    Marital_status LIKE 'Married'
        AND label = 0;

-- 6.What is the highest education level and what is the total count?
SELECT 
    Education, COUNT(Education) AS 'Count'
FROM
    creditcard
WHERE
    Education = 'Academic degree'
GROUP BY Education
ORDER BY COUNT(Education) DESC;


-- 7.Between married males and females, who is having more bad credit?
#Here 1 is male and 0 is female
SELECT 
    Gender,
    CASE
        WHEN Gender = 0 THEN 'Female'
        ELSE 'Male'
    END AS 'SEX',
    Marital_status,
    COUNT(label) AS 'Count of Rejections'
FROM
    creditcard
WHERE
    UPPER(Marital_status) LIKE 'MARRIED'
        AND label = 0
GROUP BY Gender , Marital_status
ORDER BY COUNT(label) DESC
