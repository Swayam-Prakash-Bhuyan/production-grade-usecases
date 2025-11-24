# AWK Log Analysis — Simple Solutions

This project shows how to analyze log files using very simple AWK commands.

---

## Task 1 — Unique IPs
```
awk '{ for(i=1;i<=NF;i++) if($i ~ /[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+/) print $i }' user_activity.log | sort -u
```

---

## Task 2 — Usernames
```
awk '{
  for (i = 1; i <= NF; i++) {
    if ($i ~ /user[0-9]+/) print $i
  }
}' user_activity.log | sort -u

```

---

## Task 3 — Status Code Counts
```
awk '{
    if (match($0, /[0-9]{3}$/)) {
        code = substr($0, RSTART, RLENGTH)
        count[code]++
    }
}
END {
    for (c in count)
        print c, count[c]
}' user_activity.log | sort -n
```

---

## Task 4 — Failed Logins (403)
```
awk '/403/ {print $0}' user_activity.log
```

---

## Task 5 — Summary Report
```
awk '
{
  # Extract username
  for (i = 1; i <= NF; i++) {
    if ($i ~ /user[0-9]+/) {
      user = $i
      gsub(/[^A-Za-z0-9]/, "", user)   # remove [ ] , " etc.
      users[user]++
    }

    # Count status codes
    if ($i ~ /^[0-9][0-9][0-9]$/) {
      if ($i == 200) success++
      if ($i == 403 || $i == 404) failed++
    }
  }
}
END {
  print "===== SUMMARY REPORT ====="

  # Total unique users
  uniq = 0
  for (u in users) uniq++
  print "Total Unique Users:", uniq
  print ""

  # Requests per user
  print "Total Requests Per User:"
  for (u in users)
    print "  " u ": " users[u]
  print ""

  print "Total Successful Requests (200):", success
  print "Total Failed Requests (403 + 404):", failed
}
' user_activity.log
```

---



awk 'for(i=1;i<=NF,i++)
if(i ~ /[0-9]\.[0-9]\.[0-9]\.[0-9]/)
print $i' user_activity.log | sort -u