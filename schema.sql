-- Users table
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL  -- 'student' or 'admin'
);

-- Students table
CREATE TABLE IF NOT EXISTS student (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    roll_no TEXT NOT NULL,
    department TEXT NOT NULL,
    skills TEXT,
    resume_path TEXT,
    FOREIGN KEY(user_id) REFERENCES user(id)
);

-- Admin table
CREATE TABLE IF NOT EXISTS admin (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    department TEXT NOT NULL
);

-- Jobs table
CREATE TABLE IF NOT EXISTS job (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name TEXT NOT NULL,
    role TEXT NOT NULL,
    salary TEXT,
    eligibility TEXT,
    location TEXT
);

-- Applications table
CREATE TABLE IF NOT EXISTS application (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    job_id INTEGER NOT NULL,
    status TEXT DEFAULT 'Applied',
    FOREIGN KEY(student_id) REFERENCES student(id),
    FOREIGN KEY(job_id) REFERENCES job(id)
);

-- Contact Messages table
CREATE TABLE IF NOT EXISTS contact_message (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    message TEXT NOT NULL
);
