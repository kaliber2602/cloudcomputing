CREATE DATABASE studentdb;
USE studentdb;

CREATE TABLE students
(
    id INT
    AUTO_INCREMENT PRIMARY KEY,
 student_id VARCHAR
    (10),
 fullname VARCHAR
    (100),
 dob DATE,
 major VARCHAR
    (50)
);

    INSERT INTO students
        (student_id,fullname,dob,major)
    VALUES
        ('SV01', 'Nguyen Van A', '2002-01-01', 'IT'),
        ('SV02', 'Tran Van B', '2002-02-02', 'CS'),
        ('SV03', 'Le Van C', '2002-03-03', 'SE');
