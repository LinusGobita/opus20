use master;

If(db_id(N'weatherdata') IS NULL)
begin
	create database weatherdata;
end

use weatherdata;
go

CREATE TABLE time (
  idMeasureTime int NOT NULL IDENTITY(1,1),
  dateTime      datetime NOT NULL UNIQUE,
  PRIMARY KEY (idMeasureTime));

CREATE TABLE measureType (
  idMeasureType   int NOT NULL IDENTITY(1,1),
  channel        int NOT NULL UNIQUE,
  name           varchar(30) NOT NULL,
  offset		 varchar(5),
  unit			 varchar(5),
  PRIMARY KEY (idMeasureType));
go


CREATE TABLE value (
  idValue       int NOT NULL IDENTITY(1,1),
  idDevice      int NOT NULL,
  idChannel     int NOT NULL,
  idLocation    int NOT NULL,
  idMeasureTime int NOT NULL,
  idMeasureType  int NOT NULL,
  value         decimal(9, 3),
  PRIMARY KEY (idValue));

CREATE TABLE device (
  idDevice int NOT NULL IDENTITY(1,1),
  hostname varchar(20),
  mac      varchar(12) NOT NULL UNIQUE,
  PRIMARY KEY (idDevice));


CREATE TABLE location (
  idLocation int NOT NULL IDENTITY(1,1),
  labor      varchar(20) NOT NULL,
  location   varchar(30),
  PRIMARY KEY (idLocation));


ALTER TABLE value ADD CONSTRAINT FK_Value_Device    FOREIGN KEY (idDevice) REFERENCES device (idDevice);
ALTER TABLE value ADD CONSTRAINT FK_Value_Channel   FOREIGN KEY (idMeasureType) REFERENCES measureType (idMeasureType);
ALTER TABLE value ADD CONSTRAINT FK_Value_Location  FOREIGN KEY (idLocation) REFERENCES location (idLocation);
ALTER TABLE value ADD CONSTRAINT FK_Value_MeasureTime   FOREIGN KEY (idMeasureTime) REFERENCES time (idMeasureTime);