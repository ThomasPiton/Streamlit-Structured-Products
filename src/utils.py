from datetime import date, timedelta

def get_last_business_day(ref_date: date) -> date:
    # If Saturday → go back 1 day; if Sunday → go back 2 days
    if ref_date.weekday() == 5:  # Saturday
        return ref_date - timedelta(days=1)
    elif ref_date.weekday() == 6:  # Sunday
        return ref_date - timedelta(days=2)
    return ref_date

# def get_last_business_day_minus_one(ref_date: date) -> date:
#     # Step 1: Get last business day
#     if ref_date.weekday() == 5:      # Saturday → last business day = Friday
#         last_bd = ref_date - timedelta(days=1)
#     elif ref_date.weekday() == 6:    # Sunday → last business day = Friday
#         last_bd = ref_date - timedelta(days=2)
#     else:
#         last_bd = ref_date

#     # Step 2: Go back 1 more business day
#     if last_bd.weekday() == 0:       # Monday → previous business day = Friday
#         return last_bd - timedelta(days=3)
#     else:
#         return last_bd - timedelta(days=1)