# utils/text_utils.py
import re
from typing import Tuple, Optional

money_re = re.compile(r'([\$£€])\s*([\d,]+(?:\.\d{1,2})?)')
range_re = re.compile(r'([\$£€])\s*([\d,]+)\s*[-–to]+\s*([\$£€])?\s*([\d,]+)')

def parse_salary(salary_raw: str) -> Tuple[Optional[float], Optional[float], Optional[str]]:
    if not salary_raw:
        return None, None, None
    s = salary_raw.replace(",", "")
    # look for range like $115000 - $140000
    m = range_re.search(s)
    if m:
        cur1, a, cur2, b = m.groups()
        currency = cur1 or cur2
        try:
            return float(a), float(b), currency
        except:
            pass
    # single number
    m2 = money_re.search(s)
    if m2:
        cur, n = m2.groups()
        try:
            return float(n), None, cur
        except:
            pass
    return None, None, None
