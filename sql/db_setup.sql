--USERS TABLE SETUP
CREATE TABLE USERS (
    USER_ID BIGSERIAL PRIMARY KEY,
    FIRST_NAME varchar(20) NOT NULL,
    LAST_NAME varchar(20) NOT NULL,
    EMAIL text NOT NULL,
    PWD text NOT NULL,
    TERMS BOOLEAN NOT NULL,
    CREATED timestamp NOT NULL
);

--WORKOUTS TABLE SETUP
CREATE TABLE WORKOUTS (
    WORKOUT_ID INT PRIMARY KEY,
    WORKOUT_TYPE VARCHAR(20) NOT NULL,
    WORKOUT_NAME VARCHAR(50) NOT NULL,
    WORKOUT_DESC TEXT NOT NULL,
    DIST FLOAT,
    DIST_KM FLOAT,
    PHASE VARCHAR(20) NOT NULL,
    DIST_LEVEL_MIN FLOAT NOT NULL,
    DIST_LEVEL_MAX FLOAT NOT NULL,
    RACE FLOAT NOT NULL
);

--COPYING WORKOUTS.CSV INTO WORKOUTS TABLE FROM PSQL CLI
\copy workouts from 'C:\Users\scottn\Documents\git_repos\MachineCoaching\workouts\workouts.csv' with DELIMITER ',' CSV HEADER;