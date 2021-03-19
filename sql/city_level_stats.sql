WITH sub1 AS (
    SELECT entries,
           exits,
        /* CAST(date AS DATE) AS date1,*/
           (date :: DATE || ' ' || time) :: timestamp AS date_time,
           TO_CHAR(date :: DATE, 'yyyy-mm')           AS period,
           (station || '-' || linename)               AS station1,
           (unit || '-' || "C/A" || '-' || scp)       AS turnstile
    FROM mta.turnstile_data
    WHERE
        /*Only the three divisions that are part of the NYC subway system*/
        division IN ('BMT', 'IND', 'IRT')
        /* Only need data starting 2020; 2019 is needed to YoY calculations */
      AND date :: DATE > '2018-12-31'
        /* Filter out records that were taken randomly */
      AND (
            (time LIKE '%:00:00')
            OR (time LIKE '%:30:00')
        )
    ORDER BY station1,
             turnstile,
             date_time
),
     turnstile_count AS (
         SELECT turnstile
         FROM sub1
         GROUP BY turnstile
             /*Remove turnstiles that only appear occationally*/
         HAVING COUNT(turnstile) > 600
     ),
     sub2 AS (
         SELECT *,
                entries - LAG(entries, 1) OVER (PARTITION BY turnstile) AS entries_usage,
                exits - LAG(exits, 1) OVER (PARTITION BY turnstile)     AS exits_usage
         FROM sub1
         WHERE turnstile IN (
             SELECT DISTINCT turnstile
             FROM turnstile_count
         )
     ),
     result_sub AS (
         SELECT period,
                SUM(abs(entries_usage)) AS entries_usage1,
                SUM(abs(exits_usage))   AS exits_usage1
         FROM sub2
         WHERE (entries_usage IS NOT NULL)
           AND (exits_usage IS NOT NULL)
           AND (abs(entries_usage) < 7200)
           AND (abs(exits_usage) < 7200)
         GROUP BY period
         ORDER BY period
     ),
     result_sub2 AS (
         SELECT *,
                LAG(entries_usage1, 12) OVER (
                    ORDER BY
                        period
                    ) AS entries_usage1_lag,
                LAG(exits_usage1, 12) OVER (
                    ORDER BY
                        period
                    ) AS exits_usage1_lag
         FROM result_sub
     )
SELECT 'New York City'                     AS area,
       (period || '-01')                   AS period1,
       entries_usage1 / entries_usage1_lag AS entry_usage_yoy,
       exits_usage1 / exits_usage1_lag     AS exit_usage_yoy
FROM result_sub2
WHERE (entries_usage1_lag IS NOT NULL)
  AND (exits_usage1_lag IS NOT NULL)