def mins_to_meters(m, s):
    base10_sec = round(s/60, 3)
    base10_min = m+base10_sec
    seconds = base10_min*60
    metersps = 1609.34/seconds
    return metersps

def meters_to_mins(mps):
    sec_per_mile = round(1609.34/mps, 3)
    base10_min = sec_per_mile/60
    mins = int(base10_min)
    sec = round(base10_min%1, 3)*60
    return mins, sec
