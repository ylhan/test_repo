import psycopg2
import time

params = {
    "database": "core_db",
    "user": "root",
    "password": "z78SNNSHsQg8tN16gTNR",
    "host": "localhost",
    "port": "1111",
}

conn = psycopg2.connect(**params)
curs = conn.cursor()

def query(limit, offset):
    q = f"""WITH TRADABLE_BONDS AS (SELECT *
				FROM REFERENCE_DATA
				WHERE STATUS = 'outstanding'::BOND_STATUS),
		RISK_POLICIES AS (SELECT ASSET_CLASS,
					RISK_GROUP_ID,
					ENFORCE_ALLOWLIST
			FROM RISK_GROUP_ASSET_POLICY RGAP
			WHERE RGAP.ARCHIVED_AT IS NULL AND RGAP.RISK_GROUP_ID='018973c8-d1b2-38df-e14a-06f0c9dfabdf'),
		ALLOW_LISTS AS (SELECT RISK_GROUP_ID,
					ISIN,
					BOND_TYPE
			FROM RISK_GROUP_ALLOW_LIST RGAL
					JOIN RISK_POLICIES RP USING (RISK_GROUP_ID)
			WHERE RP.ENFORCE_ALLOWLIST
			AND RGAL.ARCHIVED_AT IS NULL
			AND RGAL.BOND_TYPE=RP.ASSET_CLASS),
		ALLOWED_BONDS AS (
			SELECT TB.*
			FROM TRADABLE_BONDS TB
			JOIN ALLOW_LISTS AL ON TB.TYPE = AL.BOND_TYPE AND TB.ISIN = AL.ISIN
			UNION
			SELECT TB2.*
			FROM TRADABLE_BONDS TB2
			JOIN RISK_POLICIES RP2
				ON TB2.TYPE = RP2.ASSET_CLASS AND RP2.ENFORCE_ALLOWLIST IS NOT TRUE)
		SELECT
		    ISIN, CUSIP
		FROM ALLOWED_BONDS
        ORDER BY ISIN
LIMIT {limit}
OFFSET {offset};"""
    return q

for trials in range(10):
    # for lim in (1000, 10000):          
    offset = 0 
    limit = 1000
    iteration = 0
    curs.execute(query(limit, offset))
    while resp := curs.fetchall(): 
        start = time.time()
        curs.execute(query(limit, offset))
        end = time.time()
        print(f"Trial {trials}; limit {limit}; offset {offset}; time {end - start}")
        iteration += 1
        offset = limit * iteration
print("database connected")