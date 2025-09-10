-- Beta vs market (approximate, using covariance/variance if available in your SQL engine).
-- SQLite lacks COVAR/VAR by default: compute beta in Power BI or via Python.
-- This file exists to document intended logic for engines that support it.

-- Crisis day performance (median item return on bottom 20% market days) should be computed in Power BI or Python.
