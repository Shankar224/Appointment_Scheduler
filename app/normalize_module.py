import dateparser
from datetime import datetime, timedelta
import pytz
from typing import Optional, Dict, Union
import calendar
import re

KOLKATA = pytz.timezone("Asia/Kolkata")
DEFAULT_TIME = "09:00"

def _get_next_weekday(current_date: datetime, weekday: int) -> datetime:
    """Get the next occurrence of a given weekday."""
    days_ahead = weekday - current_date.weekday()
    if days_ahead <= 0:  # Target day already happened this week
        days_ahead += 7
    return current_date + timedelta(days=days_ahead)

def _parse_relative_day(phrase: str, base_dt: datetime) -> Optional[datetime]:
    """Handle relative day expressions like 'next Friday'."""
    phrase = phrase.lower()
    weekdays = {day.lower(): i for i, day in enumerate(calendar.day_name)}
    
    words = phrase.split()
    if len(words) == 2 and words[0] in ['next', 'this'] and words[1] in weekdays:
        weekday = weekdays[words[1]]
        dt = _get_next_weekday(base_dt, weekday)
        if words[0] == 'next':
            # For "next Friday", if today is Friday, we want next week's Friday
            if base_dt.weekday() == weekday:
                dt += timedelta(days=7)
        return dt
    return None

def _parse_time(time_str: str) -> Optional[datetime]:
    """Parse time strings like '3pm', '15:00', '3:30pm'"""
    time_str = time_str.lower().strip()
    
    # Remove 'at' prefix if present
    time_str = re.sub(r'^at\s+', '', time_str)
    
    # Try common time formats
    time_formats = [
        ('%I%p', r'^\d{1,2}(?:am|pm)$'),  # 3pm
        ('%I:%M%p', r'^\d{1,2}:\d{2}(?:am|pm)$'),  # 3:30pm
        ('%H:%M', r'^\d{2}:\d{2}$'),  # 15:00
    ]
    
    # Clean up the time string
    time_str = time_str.replace(' ', '')
    
    for fmt, pattern in time_formats:
        if re.match(pattern, time_str):
            try:
                # Use today's date as base, we only care about the time part
                return datetime.strptime(time_str, fmt)
            except ValueError:
                continue
    
    return None

def _parse_with_base(phrase: Optional[str], base_dt: datetime) -> Optional[datetime]:
    """Parse date/time with smart handling of relative and absolute expressions."""
    if not phrase:
        return None
    
    # First try handling relative day expressions
    if isinstance(phrase, str):
        relative_dt = _parse_relative_day(phrase, base_dt)
        if relative_dt:
            return relative_dt
    
    # Then try dateparser with different settings
    settings = {
        'RELATIVE_BASE': base_dt,
        'PREFER_DATES_FROM': 'future',
        'TIMEZONE': 'Asia/Kolkata',
        'RETURN_AS_TIMEZONE_AWARE': True,
        'PREFER_DAY_OF_MONTH': 'first'
    }

    parsed = dateparser.parse(phrase, settings=settings)
    if not parsed:
        settings['DATE_ORDER'] = 'DMY'
        parsed = dateparser.parse(phrase, settings=settings)
    
    return parsed

def normalize(date_phrase: Optional[str], time_phrase: Optional[str]) -> Dict[str, Union[dict, str, float]]:
    """
    Convert date/time phrases to ISO format with timezone handling.
    Returns a dict with normalized values or clarification status.
    """
    now = datetime.now(KOLKATA)
    
    # Handle date parsing
    parsed_date = _parse_with_base(date_phrase, now)
    
    # Handle time parsing
    if time_phrase:
        parsed_time = _parse_time(time_phrase)
        if parsed_time:
            time_part = parsed_time.time()
        else:
            # Fallback to dateparser if our custom parsing fails
            parsed_time = dateparser.parse(time_phrase)
            if parsed_time:
                time_part = parsed_time.time()
            else:
                return {"status": "needs_clarification", "message": "Invalid time format"}
    else:
        time_part = datetime.strptime(DEFAULT_TIME, "%H:%M").time()
    
    if not parsed_date:
        return {"status": "needs_clarification", "message": "Invalid or missing date"}

    # Combine date and time
    final_dt = KOLKATA.localize(datetime.combine(parsed_date.date(), time_part))
    
    # If the resulting datetime is in the past, assume next occurrence
    if final_dt < now:
        if date_phrase and 'next' not in date_phrase.lower():
            final_dt += timedelta(days=7)

    return {
        "normalized": {
            "date": final_dt.date().isoformat(),
            "time": final_dt.time().strftime("%H:%M"),
            "tz": "Asia/Kolkata"
        },
        "normalization_confidence": 0.9
    }