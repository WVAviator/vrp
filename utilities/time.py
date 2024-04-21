def time_str_to_int(time_str: str) -> int:
    if time_str == "EOD":
        return 1440
    time, period = time_str.split(" ")
    hours_str, minutes_str = time.split(":")
    hours = int(hours_str)
    minutes = int(minutes_str)
    if period.upper() == "PM":
        hours += 12
    return hours * 60 + minutes


def time_int_to_str(time: int) -> str:
    hours = time // 60
    minutes = time % 60
    period = "AM"
    if hours >= 12:
        period = "PM"
        if hours > 12:
            hours -= 12
    if hours == 0:
        hours = 12
    return f"{hours}:{minutes:02d} {period}"


def time_float_to_str(time: float) -> str:
    return time_int_to_str(int(time))
