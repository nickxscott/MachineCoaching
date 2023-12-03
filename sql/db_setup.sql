--CREATE USER TABLE

CREATE OR REPLACE TABLE MC_DB.APP_DATA.USERS (
    USER_ID integer autoincrement start 1 increment 1, -- auto incrementing IDs
    FIRST_NAME varchar (100),  -- variable string column
    LAST_NAME varchar (100),  -- variable string column
    DIST_PREFERENCE varchar(2), -- mi/km
    CREATED timestamp
);

--INSERT FIRST USER
INSERT INTO USERS (FIRST_NAME, LAST_NAME, DIST_PREFERENCE, CREATED) SELECT 'Nick' , 'Scott', 'mi', SYSDATE()

--CREATE PLAN TABLE

CREATE OR REPLACE TABLE MC_DB.APP_DATA.PLANS (
    PLAN_ID INTEGER AUTOINCREMENT START 1 INCREMENT 1, -- auto incrementing IDs
    DATE DATE,  -- variable string column
    DAY VARCHAR (100),  -- variable string column
    WEEK INTEGER, -- mi/km
    PHASE VARCHAR (100),
    WEEKLY_MILEAGE FLOAT,
    WEEKLY_RUNS INTEGER,
    DISTANCE FLOAT,
    RUN_TYPE VARCHAR (100),
    RUN_DESC VARCHAR(16777216),
    RUN_NAME VARCHAR (100),
    PACE VARCHAR (100)
);