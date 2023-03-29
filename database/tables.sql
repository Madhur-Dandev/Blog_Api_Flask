CREATE TABLE
    blog_users(
        id INT AUTO_INCREMENT,
        user_name VARCHAR(50) NOT NULL,
        user_email VARCHAR(255) NOT NULL,
        user_password VARCHAR(255) NOT NULL,
        user_avatar VARCHAR(255) DEFAULT "",
        verified TINYINT(1) DEFAULT FALSE,
        token VARCHAR(255) DEFAULT "",
        PRIMARY KEY (id)
    );

-- CREATE TABLE

--     blog_unverified_users(

--         id INT AUTO_INCREMENT,

--         user_email VARCHAR(255) NOT NULL,

--         PRIMARY KEY (id)

--     )

CREATE TABLE
    blog_blacklisted_tokens(
        id int AUTO_INCREMENT,
        token VARCHAR(255) NOT NULL,
        PRIMARY KEY (id)
    );

CREATE TABLE
    new_blogs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        blog_title VARCHAR(500),
        blog_description VARCHAR(2000) NOT NULL,
        blog_image VARCHAR(255),
        data_created DATETIME DEFAULT CURRENT_TIMESTAMP,
        likes INT DEFAULT 0,
        dislikes INT DEFAULT 0,
        user_id INT NOT NULL
    );

CREATE TABLE
    blog_comments (
        id INT AUTO_INCREMENT PRIMARY KEY,
        blog_id INT NOT NULL,
        user_id INT NOT NULL,
        comment_body VARCHAR(1000) NOT NULL
    );

CREATE TABLE
    blog_comment_replies(
        id INT AUTO_INCREMENT PRIMARY KEY,
        blog_id INT NOT NULL,
        user_id INT NOT NULL,
        comment_id INT NOT NULL,
        reply_body VARCHAR(1000) NOT NULL
    );