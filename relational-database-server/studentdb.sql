CREATE DATABASE studentdb;
USE studentdb;

CREATE TABLE students (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id VARCHAR(10),
    fullname VARCHAR(100),
    dob DATE,
    major VARCHAR(50)
);

INSERT INTO students (student_id, fullname, dob, major) VALUES 
('SV001', 'Nguyen Van A', '2002-03-15', 'Computer Science'),
('SV002', 'Tran Thi B', '2001-11-02', 'Data Science'),
('SV003', 'Le Van C', '2002-07-20', 'Cybersecurity');