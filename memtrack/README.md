# Memory Usage Search Guide

This guide explains how to query the memory statistics database to find the top 10 memory users at specific times.

**Database Path:** `/home/ubuntu/code/gt/tgk/ubu/sys/mem_stats.db`

## Prerequisites

Ensure you have `sqlite3` installed. You can access the database using:

```bash
sqlite3 /home/ubuntu/code/gt/tgk/ubu/sys/mem_stats.db
```

## Queries

### General Strategy

Since data is collected at intervals, we first need to find the closest snapshot time to our target time, and then query the top processes for that specific timestamp.

### 1. Find the Closest Timestamp

To find the actual recorded timestamp closest to your target time, use the following query (replace `TARGET_TIME` with your desired time, e.g., `'2026-01-16 18:15:00'`):

```sql
SELECT timestamp 
FROM memory_log 
ORDER BY ABS(strftime('%s', timestamp) - strftime('%s', 'TARGET_TIME')) ASC 
LIMIT 1;
```

### 2. Get Top 10 Memory Users

Once you have the `FOUND_TIMESTAMP` from the previous step, use it to get the top processes:

```sql
SELECT pid, user, command, rss_mb, pmem 
FROM memory_log 
WHERE timestamp = 'FOUND_TIMESTAMP' 
ORDER BY rss_mb DESC 
LIMIT 10;
```

---

## Specific Examples for January 16, 2026

### 6:15 PM (18:15) January 16, 2026

**Step 1: Find closest time**
```sql
SELECT timestamp FROM memory_log ORDER BY ABS(strftime('%s', timestamp) - strftime('%s', '2026-01-16 18:15:00')) ASC LIMIT 1;
```

**Step 2: Get data** (Replace `'FOUND_TIMESTAMP'` with the result from Step 1)
```sql
SELECT pid, user, command, rss_mb, pmem 
FROM memory_log 
WHERE timestamp = 'FOUND_TIMESTAMP' 
ORDER BY rss_mb DESC 
LIMIT 10;
```

### 5:30 PM (17:30) January 16, 2026

**Step 1: Find closest time**
```sql
SELECT timestamp FROM memory_log ORDER BY ABS(strftime('%s', timestamp) - strftime('%s', '2026-01-16 17:30:00')) ASC LIMIT 1;
```

**Step 2: Get data** (Replace `'FOUND_TIMESTAMP'` with the result from Step 1)
```sql
SELECT pid, user, command, rss_mb, pmem 
FROM memory_log 
WHERE timestamp = 'FOUND_TIMESTAMP' 
ORDER BY rss_mb DESC 
LIMIT 10;
```


SELECT pid, user, command, rss_mb, pmem 
FROM memory_log 
WHERE timestamp = '2026-01-16 17:30:14' 
ORDER BY rss_mb DESC 
LIMIT 10;