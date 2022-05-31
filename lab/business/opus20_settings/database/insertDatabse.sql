
use weatherdata
go

INSERT INTO weatherdata.dbo.device(hostname, mac)
			values	('wetterstation1', 'EC986C0A584A'),
					('wetterstation2', 'EC986C0A584B'),
					('wetterstation3', 'EC986C0A584C'),
					('wetterstation4', 'EC986C0A5851');
go


INSERT INTO weatherdata.dbo.location(labor, location)
			values  ('Hochstrom', 'Halle1'),
					('Mechanik', 'Halle1'),
					('Mechanik', 'Halle2'),
					('Mechanik', 'Keller'),
					('Hochspannung', 'Halle1'),
					('Hochspannung', 'Halle2'),
					('Kalibrierstelle', 'Oerlikon');
go



INSERT INTO weatherdata.dbo.measureType(channel, name, unit, offset)
			values
					(100, 'CUR temperature', '°C', '±10.0'),
					(120, 'MIN temperature', '°C', '±10.0'),
					(140, 'MAX temperature', '°C', '±10.0'),
					(160, 'AVG temperature', '°C', '±10.0'),
                    (105, 'CUR temperature', '°F', '0.0'),
                	(125, 'MIN temperature', '°F', '0.0'),
                    (145, 'MAX temperature', '°F', '0.0'),
                    (165, 'AVG temperature', '°F', '0.0'),
                    (110, 'CUR dewpoint','°C', '0.0'),
                    (130, 'MIN dewpoint','°C', '0.0'),
                    (150, 'MAX dewpoint','°C', '0.0'),
                    (170, 'AVG dewpoint','°C', '0.0'),
                    (115, 'CUR dewpoint','°F', '0.0'),
                    (135, 'MIN dewpoint','°F', '0.0'),
                    (155, 'MAX dewpoint','°F', '0.0'),
                    (175, 'AVG dewpoint','°F', '0.0'),
                    (200, 'CUR relative humidity', '%','±30.0'),
                    (220, 'MIN relative humidity', '%','±30.0'),
                    (240, 'MAX relative humidity', '%','±30.0'),
                    (260, 'AVG relative humidity', '%','±30.0'),
                    (205, 'CUR absolute humidity', 'g/m³', '0.0'),
                    (225, 'MIN absolute humidity', 'g/m³', '0.0'),
                    (245, 'MAX absolute humidity', 'g/m³', '0.0'),
                    (265, 'AVG absolute humidity', 'g/m³', '0.0'),
                    (300, 'CUR abs. air pressure', 'hPa','±10.0'),
                    (320, 'MIN abs. air pressure', 'hPa','±10.0'),
                    (340, 'MAX abs. air pressure', 'hPa','±10.0'),
                    (360, 'AVG abs. air pressure', 'hPa','±10.0'),
                    (305, 'CUR abs. air pressure', 'hPa','0.0'),
                    (325, 'MIN abs. air pressure', 'hPa','0.0'),
                    (345, 'MAX abs. air pressure', 'hPa','0.0'),
                    (365, 'AVG abs. air pressure', 'hPa','0.0'),
                    (10020, 'CUR battery voltage', 'V','0.0'),
                    (10040, 'MIN battery voltage', 'V','0.0'),
                    (10060, 'MAX battery voltage', 'V','0.0'),
                    (10080, 'AVG battery voltage', 'V','0.0');
go