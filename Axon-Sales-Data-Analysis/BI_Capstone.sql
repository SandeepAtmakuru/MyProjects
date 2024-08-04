Use Axon;
-- New table Creation
CREATE TABLE details (
    customerNumber INT NOT NULL,
    phone VARCHAR(50),
    city VARCHAR(50),
    state VARCHAR(50),
    postalcode VARCHAR(50),
    country VARCHAR(50),
    FOREIGN KEY (customerNumber)
        REFERENCES customers (customerNumber)
);
-- inserting values
insert into details(customerNumber,phone,city,state,postalcode,country)
select customerNumber,phone,city,state,postalcode,country from customers;
-- Verifying the data
select count(*) over(),customername,c.customerNumber,d.phone,d.city,d.state,d.postalcode,d.country from customers c
inner join details d on c.customernumber=d.customernumber ;


-- adding new columns as per requirements
alter table customers drop column phone,drop column city,drop column state,drop column postalcode,drop  column country;

alter table details add column(addressLine1 varchar(50),addressLine2 varchar(50));

-- for getting access for the updates
SET SQL_SAFE_UPDATES = 0;


UPDATE details d
        INNER JOIN
    customers c ON d.customerNumber = c.customerNumber 
SET 
    d.addressLine1 = c.addressLine1,
    d.addressLine2 = c.addressLine2;
SELECT 
    *
FROM
    details d
        INNER JOIN
    customers c ON c.customernumber = d.customernumber;

alter table customers drop column addressline1,drop column addressline2;


rename table details to customerdetails;

alter table details drop column officecode;

drop table profits;
-- New table creation
CREATE TABLE profits SELECT o.ordernumber,
    od.productCode,
    productname,
    o.orderdate,
    quantityOrdered,
    priceeach - buyprice AS profit_on_sale,
    buyprice,
    priceeach FROM
    products p
        INNER JOIN
    orderdetails od ON od.productcode = p.productcode
        INNER JOIN
    orders o ON o.ordernumber = od.ordernumber;
-- For verifying the data
SELECT 
    *
FROM
    profits
WHERE
    productname = '1937 Horch 930V Limousine';


drop table Managers;

create table Managers

SELECT 
    e1.employeenumber AS ManagerEmployeeId,
    CONCAT(e1.firstname,
            ' ',
            e1.lastname,
            ' ',
            e1.jobtitle) AS Manager,
    e2.employeenumber AS EmployeeId,
    CONCAT(e2.firstname, e2.lastname) AS Employee,
    city,
    country
FROM
    employees e1
        RIGHT JOIN
    employees e2 ON e1.employeenumber = e2.reportsTo
        INNER JOIN
    offices o ON o.officecode = e1.officecode;

select * from managers;
