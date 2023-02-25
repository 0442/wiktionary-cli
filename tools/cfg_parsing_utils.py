import re

def expiration_time_to_seconds(time_str: str) -> int:
        seconds_sum = 0

        # abbreviation and multiplier for converting to seconds
        abbrevs = {
                "y"   :  365 * 24 * 60 * 60,
                "m"   :  30 * 24 * 60 * 60,
                "w"   :  7 * 24 * 60 * 60,
                "d"   :  24 * 60 * 60,
                "h"   :  60 * 60,
                "min" :  60,
                "s"   :  1
        }

        for abbrev, multiplier in abbrevs.items():
                matches = re.finditer("([0-9]+)" + abbrev, time_str)
                if matches == None:
                        continue

                for m in matches:
                        match_str = time_str[m.start() :  m.end()].strip(abbrev)
                        seconds_sum += int(match_str) * multiplier

        return seconds_sum