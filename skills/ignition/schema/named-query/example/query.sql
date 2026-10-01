SELECT batch_id, product_code, started, finished, good_count, reject_count
FROM   batch_history
WHERE  line_id = :lineId
  AND  finished >= :since
ORDER  BY {sortCol} DESC
